package handlers

import (
	"errors"
	"fmt"
	"sync"
	"testing"

	"github.com/akmatori/akmatori/internal/database"
	"github.com/akmatori/akmatori/internal/services"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// Research-only SQLite outbox demonstrator. Not shipped by Akmatori.
// All time is a deterministic monotonic test clock; no live worker or Slack.
type batch40DurableChange struct {
	SourceID       string `gorm:"primaryKey;size:255"`
	EventUUID      string `gorm:"size:36;not null"`
	SlackChannelID string
	SlackThreadTS  string
	State          string `gorm:"size:24;not null"` // pending, leased, submitted, completed, posting, posted
	LeaseOwner     string
	LeaseDeadline  int64
	Attempts       int
	Response       string
	SlackReceipt   string
}

func (batch40DurableChange) TableName() string { return "batch40_research_durable_change_outbox" }

func batch40OutboxDB(path string) (*gorm.DB, error) {
	return gorm.Open(sqlite.Open("file:"+path+"?_busy_timeout=5000&_journal_mode=WAL"), &gorm.Config{})
}
func batch40OutboxCreate(db *gorm.DB, ev database.Event, c batch40DurableChange) (bool, error) {
	if ev.Kind != database.EventKindChange || ev.SourceKind != database.EventSourceSlackListener ||
		ev.UUID == "" || ev.SourceUUID == "" || ev.ExternalID == "" ||
		c.EventUUID != ev.UUID || c.SourceID != ev.SourceUUID+":"+ev.ExternalID ||
		c.SlackThreadTS == "" || c.SlackChannelID == "" {
		return false, fmt.Errorf("untrusted source/outbox provenance")
	}
	if c.State != "pending" {
		return false, fmt.Errorf("admission must start pending")
	}
	q := db.Clauses(clause.OnConflict{DoNothing: true}).Create(&c)
	return q.RowsAffected == 1, q.Error
}
func batch40OutboxClaim(db *gorm.DB, sourceID, owner string, now, duration int64) (bool, error) {
	if owner == "" || now <= 0 || duration <= 0 {
		return false, fmt.Errorf("invalid lease terms")
	}
	q := db.Model(&batch40DurableChange{}).
		Where("source_id = ? AND (state = ? OR (state = ? AND lease_deadline <= ?))",
			sourceID, "pending", "leased", now).
		Updates(map[string]interface{}{"state": "leased", "lease_owner": owner,
			"lease_deadline": now + duration, "attempts": gorm.Expr("attempts + 1")})
	return q.RowsAffected == 1, q.Error
}
func batch40OutboxAdvance(db *gorm.DB, key, owner, from, to string, now int64) (bool, error) {
	if key == "" || owner == "" {
		return false, fmt.Errorf("missing owner")
	}
	q := db.Model(&batch40DurableChange{}).
		Where("source_id = ? AND lease_owner = ? AND state = ? AND lease_deadline > ?",
			key, owner, from, now).
		Updates(map[string]interface{}{"state": to})
	return q.RowsAffected == 1, q.Error
}
func batch40OutboxEnqueueNativeEvent(t *testing.T, db *gorm.DB, suffix string) (database.Event, batch40DurableChange) {
	t.Helper()
	ev := database.Event{
		UUID: "fixture-event-" + suffix, SourceKind: database.EventSourceSlackListener, SourceUUID: "listener-channel",
		SourceType: "slack", ExternalID: "1707000000." + suffix, Kind: database.EventKindChange,
		Classification: database.EventClassificationLLM, Title: "PR ready for pre-merge review",
	}
	c := batch40DurableChange{
		SourceID: ev.SourceUUID + ":" + ev.ExternalID, EventUUID: ev.UUID, SlackChannelID: "C_CHANGES",
		SlackThreadTS: ev.ExternalID, State: "pending",
	}
	return ev, c
}

func TestBatch40DurableOutboxAtomicEventAdmissionAndRollback(t *testing.T) {
	path := t.TempDir() + "/atomic.db"
	db, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := db.AutoMigrate(&database.Event{}, &batch40DurableChange{}); err != nil {
		t.Fatal(err)
	}
	ev, c := batch40OutboxEnqueueNativeEvent(t, db, "atomic")
	expectedRollback := errors.New("crash before commit")
	err = db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Create(&ev).Error; err != nil {
			return err
		}
		ok, err := batch40OutboxCreate(tx, ev, c)
		if err != nil {
			return err
		}
		if !ok {
			return fmt.Errorf("initial outbox insertion unexpectedly skipped")
		}
		return expectedRollback
	})
	if !errors.Is(err, expectedRollback) {
		t.Fatalf("expected rollback, got %v", err)
	}
	var countEvents, countOutbox int64
	db.Model(&database.Event{}).Count(&countEvents)
	db.Model(&batch40DurableChange{}).Count(&countOutbox)
	if countEvents != 0 || countOutbox != 0 {
		t.Fatalf("transaction leaked events=%d outbox=%d", countEvents, countOutbox)
	}
	if err := db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Create(&ev).Error; err != nil {
			return err
		}
		ok, err := batch40OutboxCreate(tx, ev, c)
		if err != nil {
			return err
		}
		if !ok {
			return fmt.Errorf("committed insert skipped")
		}
		return nil
	}); err != nil {
		t.Fatal(err)
	}
	// Same Slack source key redelivered as another event: never enqueue second job.
	repeated := ev
	repeated.ID = 0 // original GORM Create populated the primary key; a real Slack redelivery has a new row
	repeated.UUID = "different-delivery-event"
	if err := db.Create(&repeated).Error; err != nil {
		t.Fatal(err)
	}
	second := c
	second.EventUUID = repeated.UUID
	ok, err := batch40OutboxCreate(db, repeated, second)
	if err != nil || ok {
		t.Fatalf("repeat re-enqueued outbox: ok=%v err=%v", ok, err)
	}
	db.Model(&database.Event{}).Count(&countEvents)
	db.Model(&batch40DurableChange{}).Count(&countOutbox)
	if countEvents != 2 || countOutbox != 1 {
		t.Fatalf("events/outbox=%d/%d, want 2/1", countEvents, countOutbox)
	}
	reopen, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	var durable batch40DurableChange
	if err := reopen.First(&durable, "source_id = ?", c.SourceID).Error; err != nil {
		t.Fatal(err)
	}
	if durable.EventUUID != ev.UUID || durable.State != "pending" {
		t.Fatalf("non-durable intent %+v", durable)
	}
	t.Log("atomic initial Event+Outbox transaction: rollback=0/0; durable commit=1/1; duplicate delivery=2 Events / 1 job")
}

func TestBatch40DurableOutboxLeaseExpiryRecoversLostDispatch(t *testing.T) {
	path := t.TempDir() + "/leased.db"
	first, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := first.AutoMigrate(&database.Event{}, &database.AgentRun{}, &database.Memory{}, &database.Skill{}, &batch40DurableChange{}); err != nil {
		t.Fatal(err)
	}
	ev, c := batch40OutboxEnqueueNativeEvent(t, first, "lease")
	if err := first.Transaction(func(tx *gorm.DB) error {
		if err := tx.Create(&ev).Error; err != nil {
			return err
		}
		_, err := batch40OutboxCreate(tx, ev, c)
		return err
	}); err != nil {
		t.Fatal(err)
	}
	ok, err := batch40OutboxClaim(first, c.SourceID, "dead-worker", 100, 50)
	if err != nil || !ok {
		t.Fatalf("original lease: ok=%v err=%v", ok, err)
	}
	// Crash before PrepareRequestScope/BeginRun/WS send. A second process,
	// simulated by a fresh separate SQLite connection, can reclaim after expiry.
	restarted, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	ok, err = batch40OutboxClaim(restarted, c.SourceID, "new-worker", 120, 50)
	if err != nil || ok {
		t.Fatalf("reclaimed unexpired lease: ok=%v err=%v", ok, err)
	}
	ok, err = batch40OutboxClaim(restarted, c.SourceID, "new-worker", 151, 50)
	if err != nil || !ok {
		t.Fatalf("expired lease was not reclaimable: ok=%v err=%v", ok, err)
	}
	ok, err = batch40OutboxAdvance(first, c.SourceID, "dead-worker", "leased", "submitted", 155)
	if err != nil || ok {
		t.Fatalf("expired stale worker stole lease: ok=%v err=%v", ok, err)
	}
	// Use first-party Akmatori request APIs, not a fabricated worker record.
	previous := database.DB
	database.DB = restarted
	defer func() { database.DB = previous }()
	svc := services.NewSkillService(t.TempDir(), nil, nil, nil)
	scope, dir, err := svc.PrepareRequestScope("incident-manager", ev.UUID)
	if err != nil || scope != ev.UUID || dir == "" {
		t.Fatalf("original PrepareRequestScope: %s %s %v", scope, dir, err)
	}
	runID, err := svc.BeginRun(services.RunStart{
		ScopeUUID: scope, EventUUID: ev.UUID, SourceKind: database.EventSourceSlackListener,
		SourceUUID: ev.SourceUUID, RootSkill: "incident-manager",
		SlackChannelID: c.SlackChannelID, SlackThreadTS: c.SlackThreadTS,
	})
	if err != nil {
		t.Fatal(err)
	}
	ok, err = batch40OutboxAdvance(restarted, c.SourceID, "new-worker", "leased", "submitted", 155)
	if err != nil || !ok {
		t.Fatalf("winner cannot mark submitted: %v %v", ok, err)
	}
	// Use the original durable DB completion primitive directly. SkillService.FinishRun
	// also schedules asynchronous memory-file regeneration, irrelevant to this
	// recovery contract and unsafe to race against t.TempDir cleanup.
	if err := database.FinishAgentRun(restarted, runID, database.AgentRunResult{SessionID: "offline-fixture", Response: "Read-only review fixture: risk, tests, rollback"}); err != nil {
		t.Fatal(err)
	}
	ok, err = batch40OutboxAdvance(restarted, c.SourceID, "new-worker", "submitted", "completed", 155)
	if err != nil || !ok {
		t.Fatalf("winner cannot mark completed: %v %v", ok, err)
	}
	var runs []database.AgentRun
	if err := restarted.Find(&runs).Error; err != nil {
		t.Fatal(err)
	}
	if len(runs) != 1 || runs[0].EventUUID != ev.UUID || runs[0].Status != database.AgentRunStatusCompleted || runs[0].IncidentUUID != "" {
		t.Fatalf("recovered native request run %+v", runs)
	}
	// Completed work must not be claimed again after any lease.
	ok, err = batch40OutboxClaim(first, c.SourceID, "third-worker", 10000, 25)
	if err != nil || ok {
		t.Fatalf("completed work reclaimed: %v %v", ok, err)
	}
	var current batch40DurableChange
	restarted.First(&current, "source_id = ?", c.SourceID)
	if current.Attempts != 2 || current.LeaseOwner != "new-worker" || current.State != "completed" {
		t.Fatalf("bad lease fencing: %+v", current)
	}
	t.Log("crash before dispatch: first claimant dead, pre-expiry retry denied, post-expiry recovered by new owner; stale owner fenced; one completed first-party request run")
}

func TestBatch40DurableOutboxConcurrentLeaseFencing(t *testing.T) {
	path := t.TempDir() + "/fencing.db"
	first, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := first.AutoMigrate(&database.Event{}, &batch40DurableChange{}); err != nil {
		t.Fatal(err)
	}
	ev, c := batch40OutboxEnqueueNativeEvent(t, first, "fence")
	first.Create(&ev)
	if ok, err := batch40OutboxCreate(first, ev, c); err != nil || !ok {
		t.Fatalf("insert: %v %v", ok, err)
	}
	second, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	var wg sync.WaitGroup
	type outcome struct {
		ok  bool
		err error
	}
	outcomes := make(chan outcome, 2)
	for i, db := range []*gorm.DB{first, second} {
		wg.Add(1)
		go func(worker int, d *gorm.DB) {
			defer wg.Done()
			ok, err := batch40OutboxClaim(d, c.SourceID, fmt.Sprintf("claimant-%d", worker), 100, 50)
			outcomes <- outcome{ok, err}
		}(i, db)
	}
	wg.Wait()
	close(outcomes)
	admitted := 0
	for r := range outcomes {
		if r.err != nil {
			t.Fatalf("database claim error: %v", r.err)
		}
		if r.ok {
			admitted++
		}
	}
	if admitted != 1 {
		t.Fatalf("two independent connections admitted %d workers", admitted)
	}
	var row batch40DurableChange
	if err := second.First(&row, "source_id = ?", c.SourceID).Error; err != nil {
		t.Fatal(err)
	}
	if row.Attempts != 1 || row.State != "leased" {
		t.Fatalf("claim state %+v", row)
	}
	t.Log("two independent DB connections: one unique conditional lease claim, one rejected")
}

func TestBatch40DurableOutboxSlackPostAmbiguityFailsClosed(t *testing.T) {
	path := t.TempDir() + "/ambiguous.db"
	db, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := db.AutoMigrate(&database.Event{}, &batch40DurableChange{}); err != nil {
		t.Fatal(err)
	}
	ev, c := batch40OutboxEnqueueNativeEvent(t, db, "posting")
	db.Create(&ev)
	if ok, err := batch40OutboxCreate(db, ev, c); err != nil || !ok {
		t.Fatalf("insert: %v %v", ok, err)
	}
	ok, err := batch40OutboxClaim(db, c.SourceID, "worker-a", 100, 25)
	if err != nil || !ok {
		t.Fatalf("claim: %v %v", ok, err)
	}
	for _, transition := range [][2]string{{"leased", "submitted"}, {"submitted", "completed"}, {"completed", "posting"}} {
		ok, err = batch40OutboxAdvance(db, c.SourceID, "worker-a", transition[0], transition[1], 110)
		if err != nil || !ok {
			t.Fatalf("transition %v: %v %v", transition, ok, err)
		}
	}
	// Simulate Slack HTTP success then process crash BEFORE saving Slack receipt.
	// A second dispatcher refuses to blindly replay the post; it must reconcile.
	reopened, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	ok, err = batch40OutboxClaim(reopened, c.SourceID, "worker-b", 10000, 25)
	if err != nil || ok {
		t.Fatalf("repost falsely considered safe: ok=%v err=%v", ok, err)
	}
	var row batch40DurableChange
	if err := reopened.First(&row, "source_id = ?", c.SourceID).Error; err != nil {
		t.Fatal(err)
	}
	if row.State != "posting" || row.SlackReceipt != "" {
		t.Fatalf("uncertain post incorrectly marked delivered %+v", row)
	}
	t.Log("post-accepted-before-ACK crash remains ambiguous; blocked automatic repost, requires Slack receipt reconciliation/owner policy")
}

// Ambiguous crash after a worker has *possibly* accepted the dispatch but
// before a durable acknowledgement cannot be fixed by a lease alone.
func TestBatch40DurableOutboxSubmittedWithoutAckRequiresReconciliation(t *testing.T) {
	path := t.TempDir() + "/submitted-ambiguous.db"
	db, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := db.AutoMigrate(&database.Event{}, &database.AgentRun{}, &batch40DurableChange{}); err != nil {
		t.Fatal(err)
	}
	ev, c := batch40OutboxEnqueueNativeEvent(t, db, "submitted")
	if err := db.Create(&ev).Error; err != nil {
		t.Fatal(err)
	}
	if admitted, err := batch40OutboxCreate(db, ev, c); err != nil || !admitted {
		t.Fatalf("outbox admit=%v err=%v", admitted, err)
	}
	if ok, err := batch40OutboxClaim(db, c.SourceID, "maybe-sent", 100, 15); err != nil || !ok {
		t.Fatalf("claim=%v err=%v", ok, err)
	}
	if ok, err := batch40OutboxAdvance(db, c.SourceID, "maybe-sent", "leased", "submitted", 105); err != nil || !ok {
		t.Fatalf("mark submitted=%v err=%v", ok, err)
	}
	// Worker acceptance is unknown; this is NOT an executed worker request.
	// A blind retry could execute a second task, but permanent suppression
	// could strand an unaccepted task. Both claims are unproven here.
	reopened, err := batch40OutboxDB(path)
	if err != nil {
		t.Fatal(err)
	}
	if ok, err := batch40OutboxClaim(reopened, c.SourceID, "blind-retry", 999, 15); err != nil || ok {
		t.Fatalf("ambiguous worker state auto-replayed=%v err=%v", ok, err)
	}
	var runs int64
	if err := reopened.Model(&database.AgentRun{}).Count(&runs).Error; err != nil {
		t.Fatal(err)
	}
	if runs != 0 {
		t.Fatalf("unexpected fabricated worker execution %d", runs)
	}
	var row batch40DurableChange
	if err := reopened.First(&row, "source_id = ?", c.SourceID).Error; err != nil {
		t.Fatal(err)
	}
	if row.State != "submitted" || row.Attempts != 1 {
		t.Fatalf("ambiguous state modified %+v", row)
	}
	t.Log("worker-submitted-without-ACK is not safely replayable or safely discardable; requires stable run ID and worker receipt reconciliation")
}
