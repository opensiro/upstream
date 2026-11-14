package handlers

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/akmatori/akmatori/internal/database"
	"github.com/akmatori/akmatori/internal/services"
	"github.com/gorilla/websocket"
	"github.com/slack-go/slack"
	"github.com/slack-go/slack/slackevents"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// Experimental native fixture, not an Akmatori patch. The only original
// handler modifications are a test seam after storing the change event.
// Delivery on a real Slack workspace and real AI review are NOT tested.
type batch40ChangeClaim struct {
	SourceID  string `gorm:"primaryKey;size:255"`
	EventUUID string `gorm:"not null"`
}

func (batch40ChangeClaim) TableName() string { return "batch40_research_change_claims" }

func batch40DispatchChangeWithWorker(
	h *SlackHandler, db *gorm.DB, ev *database.Event, event *slackevents.MessageEvent,
	ch *database.Channel, body, thread string, mode string,
) error {
	if mode != "run" || ev == nil || ev.Kind != database.EventKindChange ||
		ev.SourceKind != database.EventSourceSlackListener || !ch.Enabled ||
		!ch.CanListen || !ch.CanPost || h.agentWSHandler == nil ||
		!h.agentWSHandler.IsWorkerConnected() {
		return nil
	}
	if ev.SourceUUID != ch.UUID || ev.ExternalID != event.TimeStamp || event.Channel != ch.ExternalID {
		return fmt.Errorf("listener provenance mismatch")
	}
	if ev.UUID == "" || body == "" || thread == "" {
		return fmt.Errorf("missing original event/body/thread")
	}
	// Atomically admit one dispatch per real Slack source message, not merely
	// per newly-recorded Event UUID (Slack can redeliver the same event).
	claim := &batch40ChangeClaim{SourceID: ch.UUID + ":" + event.TimeStamp, EventUUID: ev.UUID}
	tx := db.Clauses(clause.OnConflict{DoNothing: true}).Create(claim)
	if tx.Error != nil {
		return tx.Error
	}
	if tx.RowsAffected == 0 {
		return nil
	}
	// Crash after claim yields 0 work, not an exactly-once guarantee; this is
	// intentionally exposed as a fail-closed research limitation.
	scope, dir, err := h.skillService.PrepareRequestScope("incident-manager", ev.UUID)
	if err != nil {
		return err
	}
	if scope != ev.UUID || dir == "" {
		return fmt.Errorf("unexpected native request scope")
	}
	runID, err := h.skillService.BeginRun(services.RunStart{
		ScopeUUID: scope, EventUUID: ev.UUID, SourceKind: database.EventSourceSlackListener,
		SourceUUID: ch.UUID, RootSkill: "incident-manager", SlackChannelID: ch.ExternalID,
		SlackThreadTS: thread,
	})
	if err != nil {
		return err
	}
	type workerResult struct {
		response, session string
		failed            bool
	}
	finished := make(chan workerResult, 1)
	cb := IncidentCallback{
		OnCompleted:  func(sid, output string, _ int, _ int64) { finished <- workerResult{response: output, session: sid} },
		OnError:      func(message string) { finished <- workerResult{response: "worker error: " + message, failed: true} },
		OnSuperseded: func() { finished <- workerResult{response: "superseded", failed: true} },
	}
	// Test-prototype policy: tool-less review. This is NOT a general owner
	// permission system, and all actual skill/tool permission decisions remain.
	task := "Read-only pre-merge review requested: assess risks, blast radius, missing tests and rollback; NEVER merge or modify code.\nOriginal change-channel post:\n" + body
	_, err = h.agentWSHandler.StartIncident(scope, runID, task, nil, []string{}, []services.ToolAllowlistEntry{}, cb)
	if err != nil {
		return err
	}
	var result workerResult
	select {
	case result = <-finished:
	case <-time.After(4 * time.Second):
		return fmt.Errorf("fake worker did not complete")
	}
	if !h.agentWSHandler.ReleaseRun(scope, runID) {
		return fmt.Errorf("worker run was displaced")
	}
	h.finishSlackMessage(ch.ExternalID, thread, runID, event.User, body, result.response, result.response, "research adapter: fake worker protocol", result.failed, result.session)
	return nil
}

type batch40SlackPost struct{ Channel, Thread, Text string }

func TestBatch40NativeChangeWorkerToSlackThread(t *testing.T) {
	db := setupEventsHandlerDB(t)
	// Original native scope/worker code expects these normal production tables.
	if err := db.AutoMigrate(&database.Memory{}, &database.ProxySettings{}, &database.Skill{}); err != nil {
		t.Fatal(err)
	}
	if err := db.AutoMigrate(&batch40ChangeClaim{}); err != nil {
		t.Fatal(err)
	}
	var mu sync.Mutex
	var posted []batch40SlackPost
	slackServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r.ParseForm()
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Path == "/chat.postMessage" {
			mu.Lock()
			posted = append(posted, batch40SlackPost{Channel: r.FormValue("channel"), Thread: r.FormValue("thread_ts"), Text: r.FormValue("text")})
			mu.Unlock()
			_, _ = fmt.Fprint(w, `{"ok":true,"channel":"C_CHANGES","ts":"1707000099.000100","message":{"text":"ok"}}`)
			return
		}
		_, _ = fmt.Fprint(w, `{"ok":true,"messages":[]}`)
	}))
	defer slackServer.Close()
	slackClient := slack.New("research-token", slack.OptionAPIURL(slackServer.URL+"/"), slack.OptionHTTPClient(slackServer.Client()))
	ws := NewAgentWSHandler()
	wsServer := httptest.NewServer(http.HandlerFunc(ws.HandleWebSocket))
	defer wsServer.Close()
	workerConn, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(wsServer.URL, "http"), nil)
	if err != nil {
		t.Fatal(err)
	}
	defer workerConn.Close()
	for deadline := time.Now().Add(2 * time.Second); !ws.IsWorkerConnected(); {
		if time.Now().After(deadline) {
			t.Fatal("websocket worker never connected")
		}
		time.Sleep(5 * time.Millisecond)
	}
	callerCount := 0
	caller := &corrOneShotLLMCaller{respond: func(context.Context) (string, error) {
		callerCount++
		return `{"alert_name":"pre-merge change review","event_kind":"change","event_confidence":0.97,"summary":"tested on staging"}`, nil
	}}
	skillSvc := services.NewSkillService(t.TempDir(), nil, nil, nil)
	h := NewSlackHandler(slackClient, nil, ws, skillSvc, caller)
	h.SetEventService(services.NewEventService(db, caller))
	ch := &database.Channel{UUID: "channel-uuid", ExternalID: "C_CHANGES", Enabled: true, CanListen: true, CanPost: true}
	msg := &slackevents.MessageEvent{Channel: ch.ExternalID, TimeStamp: "1707000055.001100", User: "U_REVIEWER", Text: "Please review and merge https://github.com/example/repo/pull/24; tested on staging"}
	var hookErr error
	var hookMu sync.Mutex
	h.batch40ResearchChangeHook = func(ev *database.Event, e *slackevents.MessageEvent, c *database.Channel, body, thread string) {
		err := batch40DispatchChangeWithWorker(h, db, ev, e, c, body, thread, "run")
		hookMu.Lock()
		hookErr = err
		hookMu.Unlock()
	}
	done := make(chan struct{})
	go func() { defer close(done); h.handleAlertChannelMessage(msg, ch) }()
	if err := workerConn.SetReadDeadline(time.Now().Add(4 * time.Second)); err != nil {
		t.Fatal(err)
	}
	var outbound AgentMessage
	if err := workerConn.ReadJSON(&outbound); err != nil {
		t.Fatalf("actual WS worker did not receive agent task: %v", err)
	}
	if outbound.Type != AgentMessageTypeNewIncident || outbound.IncidentID == "" || outbound.RunID == "" ||
		!strings.Contains(outbound.Task, "NEVER merge") || !strings.Contains(outbound.Task, "pull/24") ||
		outbound.ToolAllowlist == nil || len(outbound.ToolAllowlist) != 0 {
		t.Fatalf("bad native worker dispatch %+v", outbound)
	}
	fakeReview := "Mock worker response: pre-merge risk summary, test evidence and rollback checklist. No merge performed."
	if err := workerConn.WriteJSON(AgentMessage{
		Type: AgentMessageTypeAgentCompleted, IncidentID: outbound.IncidentID, RunID: outbound.RunID,
		SessionID: "research-verified-fake-worker", Output: fakeReview, TokensUsed: 42,
	}); err != nil {
		t.Fatal(err)
	}
	select {
	case <-done:
	case <-time.After(4 * time.Second):
		t.Fatal("native Slack handler did not finish")
	}
	hookMu.Lock()
	gotHookErr := hookErr
	hookMu.Unlock()
	if gotHookErr != nil {
		t.Fatal(gotHookErr)
	}
	var events []database.Event
	if err := db.Find(&events).Error; err != nil {
		t.Fatal(err)
	}
	var runs []database.AgentRun
	if err := db.Find(&runs).Error; err != nil {
		t.Fatal(err)
	}
	var incidents []database.Incident
	if err := db.Find(&incidents).Error; err != nil {
		t.Fatal(err)
	}
	if len(events) != 1 || len(runs) != 1 || len(incidents) != 0 || callerCount != 1 {
		t.Fatalf("event/run/incident/classifier counts %d/%d/%d/%d", len(events), len(runs), len(incidents), callerCount)
	}
	if runs[0].EventUUID != events[0].UUID || runs[0].ScopeUUID != events[0].UUID ||
		runs[0].Status != database.AgentRunStatusCompleted || runs[0].Response != fakeReview ||
		runs[0].SlackThreadTS != msg.TimeStamp || runs[0].IncidentUUID != "" {
		t.Fatalf("native persisted run incorrect %+v", runs[0])
	}
	if _, err := lookupSlackThread(msg.TimeStamp); err != nil {
		t.Fatalf("original thread readback failed: %v", err)
	}
	mu.Lock()
	postCopy := append([]batch40SlackPost(nil), posted...)
	mu.Unlock()
	if len(postCopy) != 1 || postCopy[0].Channel != msg.Channel || postCopy[0].Thread != msg.TimeStamp ||
		!strings.Contains(postCopy[0].Text, "Mock worker response") {
		t.Fatalf("actual mock Slack API post failed %+v", postCopy)
	}
	// Redelivery of identical Slack message may create a second event, but the
	// unique source-message claim ensures it cannot dispatch a second agent run.
	h.handleAlertChannelMessage(msg, ch)
	var finalRuns int64
	if err := db.Model(&database.AgentRun{}).Count(&finalRuns).Error; err != nil {
		t.Fatal(err)
	}
	if finalRuns != 1 {
		t.Fatalf("duplicate Slack delivery produced %d agent runs", finalRuns)
	}
	mu.Lock()
	postCount := len(posted)
	mu.Unlock()
	if postCount != 1 {
		t.Fatalf("duplicate Slack delivery produced %d Slack replies", postCount)
	}
	t.Logf("native WS frame=new_incident run=%s enabled_skills=%d tool_allowlist=%d", outbound.RunID, len(outbound.EnabledSkills), len(outbound.ToolAllowlist))
	t.Logf("actual first-party finishSlackMessage posted=%d thread=%s; events_first=1 classifier_first=1; runs=1 incidents=0", postCount, msg.TimeStamp)
}

func TestBatch40ClaimAtomicIndependentConnections(t *testing.T) {
	// Real file-backed SQLite and two independent connections simulate
	// concurrent dispatchers. Claim records prevent concurrent same Slack item
	// from being admitted by two connections; crashes after claim are pending.
	path := t.TempDir() + "/native-dispatch.db"
	db1, err := gorm.Open(sqliteOpenResearch(path), &gorm.Config{})
	if err != nil {
		t.Fatal(err)
	}
	db2, err := gorm.Open(sqliteOpenResearch(path), &gorm.Config{})
	if err != nil {
		t.Fatal(err)
	}
	if err := db1.AutoMigrate(&batch40ChangeClaim{}); err != nil {
		t.Fatal(err)
	}
	var wg sync.WaitGroup
	accepted := make(chan bool, 2)
	for _, db := range []*gorm.DB{db1, db2} {
		wg.Add(1)
		go func(d *gorm.DB) {
			defer wg.Done()
			q := d.Clauses(clause.OnConflict{DoNothing: true}).Create(&batch40ChangeClaim{SourceID: "channel-uuid:1707000055.001100", EventUUID: "initial"})
			if q.Error != nil {
				accepted <- false
				return
			}
			accepted <- q.RowsAffected == 1
		}(db)
	}
	wg.Wait()
	close(accepted)
	successes := 0
	for yes := range accepted {
		if yes {
			successes++
		}
	}
	if successes != 1 {
		t.Fatalf("independent DB claims accepted=%d, want exactly one", successes)
	}
	var count int64
	if err := db1.Model(&batch40ChangeClaim{}).Count(&count).Error; err != nil {
		t.Fatal(err)
	}
	if count != 1 {
		t.Fatalf("persisted claims=%d", count)
	}
	t.Log("independent two-connection, same source-message claim: one accepted; DB is not a work-delivery transaction")
}

func sqliteOpenResearch(path string) gorm.Dialector { return sqlite.Open(path + "?_busy_timeout=5000") }

// This intentionally failing-delivery control documents the correctness gap:
// a successful at-most-one claim before worker dispatch is NOT a durable
// outbox. A crashed claimant can strand work forever with no AgentRun.
func TestBatch40NativeAtMostOnceClaimCanStrandUndispatchedChange(t *testing.T) {
	path := t.TempDir() + "/claim-crash-gap.db"
	first, err := gorm.Open(sqliteOpenResearch(path), &gorm.Config{})
	if err != nil {
		t.Fatal(err)
	}
	if err := first.AutoMigrate(&batch40ChangeClaim{}, &database.AgentRun{}); err != nil {
		t.Fatal(err)
	}
	key := "channel-uuid:1707000055.001100"
	claim := &batch40ChangeClaim{SourceID: key, EventUUID: "original-event"}
	if err := first.Create(claim).Error; err != nil {
		t.Fatal(err)
	}
	// In-place simulated crash: no PrepareRequestScope / BeginRun / WS
	// delivery, but the reservation has already been durably committed.
	second, err := gorm.Open(sqliteOpenResearch(path), &gorm.Config{})
	if err != nil {
		t.Fatal(err)
	}
	retry := second.Clauses(clause.OnConflict{DoNothing: true}).Create(
		&batch40ChangeClaim{SourceID: key, EventUUID: "same-slack-redelivery"})
	if retry.Error != nil {
		t.Fatal(retry.Error)
	}
	if retry.RowsAffected != 0 {
		t.Fatalf("retry unexpectedly admitted a second dispatch")
	}
	var runs int64
	if err := second.Model(&database.AgentRun{}).Count(&runs).Error; err != nil {
		t.Fatal(err)
	}
	if runs != 0 {
		t.Fatalf("unexpected worker run %d", runs)
	}
	t.Log("crash-gap negative control: durable claim=1, retry admitted=0, agent_runs=0; requires lease/outbox recovery before publication")
}
