# Existing VM/host — GitHub CLI and clean patch materialization ports

**Status: source prepared / actual authorization NOT ACTIVE.**
For the bounded [two-file prepare stage](CONNECTED_MULTIFILE_STAGE.md),
the two host operations now have source-level implementations in
[`cli_host_multifile_runtime.py`](../scripts/cli_host_multifile_runtime.py).
This is **not** a new Control Plane, standalone worker or script with a
`--execute` command. Do not refer to a particular orchestration app as
the executor; the execution environment is the actual **VM or host
where the GitHub credentials are installed and permitted to be used**.

## Authenticated GitHub CLI JSON transport

`GitHubCLIJSONTransport` implements the REST port callback shape
`api(method, path, body=None)` by invoking the locally authenticated
`gh api --include --method GET|POST`. No token or credential-helper
contents are read by this module. POST request bodies are put in a
private temporary JSON file, referenced by `--input`, not embedded
in shell arguments or logs. The file is deleted after the request.

- **GET** paths are limited to `repos/OWNER/REPO...`.
- **POST** paths are limited to Git Data
  `repos/opensiro-contributions/REPO/git/{trees,commits,refs}`.
- No PATCH, DELETE, PR publication endpoint, branch force-update,
  fork creation or general GitHub write endpoint is exposed.
- Raw HTTP status from `gh api -i` remains distinct; 403 must not be
  converted to 404. No automatic retries or PAT export.

**Crucial:** a working `gh api user` or a Classic PAT scope does
**not authorize** the caller. The protected host must authenticate the
actual API principal, prove allowed destination rights, bind the
actor to a **one-use, expiring, revocable exact prepare-stage grant**,
and enforce that grant *before constructing a writer*.

## Clean, isolated local Git patch materializer

`CleanPublicGitPatchMaterializer` takes a contributor fork, exact base
commit, whole patch text and exactly two paths. Using normal
`subprocess.run([...])` argument vectors (never a shell) it:

1. Clones the **public working fork** in a disposable temporary
   checkout without committing, pushing or using a token in args.
2. Fetches/checks out the requested **exact SHA** and verifies a
   clean working tree.
3. Validates current tracked regular `100644` source file and new
   test-path constraints, rejecting symlink/nonregular modes.
4. Runs `git apply --check`, `git apply`, stages only the two
   approved paths, then verifies the complete staged path set,
   whitespace errors, file modes and actual UTF-8 postimages.
5. Returns the exact text of both resulting blobs for the
   [GitHub REST Git Trees/Commit/Ref port](REST_MULTIFILE_PATCH_PORT.md)
   to compare against the expected postimage SHA256 fingerprints
   **before** its first POST.

A failed clone, missing base commit, conflicting patch hunk,
unexpected extra file, symlink, executable mode or untrusted blob
fails closed. The checkout is discarded and there is no `git push`.

## Host installation and pilot state

A trusted VM/host can construct these three source objects:
`GitHubCLIJSONTransport` +
`CleanPublicGitPatchMaterializer` +
`GitHubRESTMultifilePatchPort`, but only after providing
a **real provider actor/capability attestor** and a separate trusted
`verify_exact_prepare / authorize_exact_stage` issuer. Those last
two protected host capabilities are **not shipped here**.

The actual [HarnessDesk V2 packet](../pilots/harnessdesk-1772/prepare-v2-handoff.json)
is still `ACTION_PREPARED_NOT_AUTHORIZED`. Its old observed
fork `development` lagged upstream; the exact two-file stage rejects
mismatched bases and proposal blockers even if the host carries a PAT.

Do not run an unattended privileged GitHub Actions workflow, silently
sync the fork, create `opensiro/fix-toolgateway-1772`, or post an
external PR on the strength of these source files alone.

## Offline tests

[`test_cli_host_multifile_runtime.py`](../tests/test_cli_host_multifile_runtime.py)
uses a **real local bare Git repository** to exercise an actual
`git apply` and verify both resulting files and patch collisions,
as well as simulated `gh api` status/payloads. A local fake Git
repository is not remote provider proof; tests do not use a PAT.
