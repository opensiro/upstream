"""At-most-one-attempt ledger for a FUTURE independently trusted CLA executor.

Offline-only: no GitHub or HTTP operations, no legal acceptance, no proof of
consent. Reservation, dispatch-intent and reported readback are never authority.
SQLite BEGIN IMMEDIATE + unique nonce hash make concurrent retries fail closed.
After dispatch-intent, uncertainty means *do not retry*, even after a crash.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import sqlite3

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NONCE = re.compile(r"[A-Za-z0-9_.:-]{16,255}\Z")
TARGET = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+\Z")

SCHEMA = """
CREATE TABLE IF NOT EXISTS cla_attempts (
  nonce_hash TEXT PRIMARY KEY,
  packet_hash TEXT NOT NULL,
  target TEXT NOT NULL,
  fork_head TEXT NOT NULL,
  phase TEXT NOT NULL CHECK (phase IN
    ('RESERVED_NO_POST','DISPATCH_BEGAN_UNCONFIRMED','READBACK_REPORTED_UNVERIFIED')),
  first_seen TEXT NOT NULL,
  last_changed TEXT NOT NULL,
  target_url TEXT,
  dispatch_count INTEGER NOT NULL DEFAULT 0 CHECK (dispatch_count IN (0,1))
)
"""


def _blocked(reason):
    return {"status": "BLOCKED", "reason": reason}


def _hash_nonce(nonce_key):
    if not isinstance(nonce_key, str) or not NONCE.fullmatch(nonce_key):
        raise ValueError("INVALID_NONCE_KEY")
    return hashlib.sha256(
        b"opensiro-cla-nonce-v1\0" + nonce_key.encode("ascii")).hexdigest()


def _validate_packet(packet_hash, target, fork_head):
    if not isinstance(packet_hash, str) or not HEX64.fullmatch(packet_hash):
        raise ValueError("INVALID_PACKET_HASH")
    if not isinstance(target, str) or not TARGET.fullmatch(target):
        raise ValueError("INVALID_TARGET_REPOSITORY")
    if not isinstance(fork_head, str) or not HEX40.fullmatch(fork_head):
        raise ValueError("INVALID_FORK_HEAD")


def _timestamp(now):
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("MISSING_TRUSTED_CURRENT_TIME")
    return now.astimezone(timezone.utc).isoformat(timespec="seconds")


class AttemptJournal:
    """A defensive operational journal, not an authority or signing service."""

    def __init__(self, path):
        self.path = Path(path)
        if str(self.path) == ":memory:" or not self.path.parent.is_dir():
            raise ValueError("PERSISTENT_DATABASE_PATH_REQUIRED")
        with self._db() as db:
            db.execute(SCHEMA)

    @contextmanager
    def _db(self):
        db = sqlite3.connect(str(self.path), timeout=15, isolation_level=None)
        try:
            db.execute("PRAGMA busy_timeout=15000")
            db.execute("PRAGMA synchronous=FULL")
            yield db
        finally:
            db.close()

    def _transition(self, *, nonce_key, packet_hash, target, fork_head,
                    now, phase, from_phase, target_url=None):
        try:
            nonce_hash = _hash_nonce(nonce_key)
            _validate_packet(packet_hash, target, fork_head)
            stamp = _timestamp(now)
        except ValueError as e:
            return _blocked(str(e))
        try:
            with self._db() as db:
                db.execute("BEGIN IMMEDIATE")
                if phase == "RESERVED_NO_POST":
                    changed = db.execute(
                        """INSERT OR IGNORE INTO cla_attempts (
                          nonce_hash,packet_hash,target,fork_head,phase,
                          first_seen,last_changed)
                          VALUES (?,?,?,?,?,?,?)""",
                        (nonce_hash, packet_hash, target, fork_head,
                         phase, stamp, stamp),
                    ).rowcount
                elif phase == "DISPATCH_BEGAN_UNCONFIRMED":
                    changed = db.execute(
                        """UPDATE cla_attempts SET phase=?,last_changed=?,
                          dispatch_count=1 WHERE nonce_hash=? AND packet_hash=?
                          AND target=? AND fork_head=? AND phase=?
                          AND dispatch_count=0""",
                        (phase, stamp, nonce_hash, packet_hash, target,
                         fork_head, from_phase),
                    ).rowcount
                else:
                    changed = db.execute(
                        """UPDATE cla_attempts SET phase=?,last_changed=?,
                          target_url=? WHERE nonce_hash=? AND packet_hash=?
                          AND target=? AND fork_head=? AND phase=?
                          AND dispatch_count=1""",
                        (phase, stamp, target_url, nonce_hash, packet_hash,
                         target, fork_head, from_phase),
                    ).rowcount
                db.execute("COMMIT")
            if not changed:
                return _blocked("NONCE_USED_OR_INVALID_STATE")
            return {"status": "RECORDED_NON_EXECUTABLE",
                    "phase": phase, "nonce_hash": nonce_hash}
        except sqlite3.Error:
            return _blocked("DURABLE_LEDGER_UNAVAILABLE")

    def reserve(self, *, nonce_key, packet_hash, target, fork_head, now):
        """Unique local claim; does not imply valid signatory approval."""
        return self._transition(
            nonce_key=nonce_key, packet_hash=packet_hash, target=target,
            fork_head=fork_head, now=now, phase="RESERVED_NO_POST",
            from_phase=None)

    def begin_attempt(self, *, nonce_key, packet_hash, target, fork_head, now):
        """Mark irreversible intent BEFORE a possible external POST.

        There is no POST here. A future executor must never retry an uncertain
        dispatch automatically; manually reconcile target-side readback.
        """
        return self._transition(
            nonce_key=nonce_key, packet_hash=packet_hash, target=target,
            fork_head=fork_head, now=now,
            phase="DISPATCH_BEGAN_UNCONFIRMED",
            from_phase="RESERVED_NO_POST")

    def record_readback(self, *, nonce_key, packet_hash, target, fork_head,
                        target_url, now):
        """Record an UNVERIFIED external URL claim, never maintainer acceptance."""
        if not isinstance(target, str) or not TARGET.fullmatch(target):
            return _blocked("INVALID_TARGET_REPOSITORY")
        if not isinstance(target_url, str):
            return _blocked("INVALID_TARGET_READBACK_URL")
        owner, repo = target.split("/")
        expected = rf"https://github\.com/{re.escape(owner)}/{re.escape(repo)}/pull/[1-9][0-9]*\Z"
        if not re.fullmatch(expected, target_url):
            return _blocked("INVALID_TARGET_READBACK_URL")
        return self._transition(
            nonce_key=nonce_key, packet_hash=packet_hash, target=target,
            fork_head=fork_head, now=now,
            phase="READBACK_REPORTED_UNVERIFIED",
            from_phase="DISPATCH_BEGAN_UNCONFIRMED",
            target_url=target_url)

    def inspect(self, nonce_key):
        try:
            nonce_hash = _hash_nonce(nonce_key)
        except ValueError as e:
            return _blocked(str(e))
        try:
            with self._db() as db:
                row = db.execute(
                    """SELECT packet_hash,target,fork_head,phase,first_seen,
                              last_changed,target_url,dispatch_count
                       FROM cla_attempts WHERE nonce_hash=?""",
                    (nonce_hash,),
                ).fetchone()
            if row is None:
                return _blocked("NONCE_NOT_FOUND")
            keys = ("packet_hash", "target", "fork_head", "phase",
                    "first_seen", "last_changed", "target_url",
                    "dispatch_count")
            return {"status": "RECORDED_NON_EXECUTABLE",
                    "nonce_hash": nonce_hash, **dict(zip(keys, row))}
        except sqlite3.Error:
            return _blocked("DURABLE_LEDGER_UNAVAILABLE")
