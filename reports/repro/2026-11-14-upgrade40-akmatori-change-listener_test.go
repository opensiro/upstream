package handlers

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/akmatori/akmatori/internal/database"
	"github.com/akmatori/akmatori/internal/services"
	"github.com/slack-go/slack"
	"github.com/slack-go/slack/slackevents"
)

// Research-only native negative-control: a listener's change-announcement
// event is stored but cannot begin a scoped, threaded agent run as requested
// by upstream issue #79. Test uses the pinned first-party handler.
func TestBatch40ListenerChangeAnnouncementStoresOnly(t *testing.T) {
	db := setupEventsHandlerDB(t)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = fmt.Fprint(w, `{"ok":true,"messages":[]}`)
	}))
	defer server.Close()
	client := slack.New("test-token", slack.OptionAPIURL(server.URL+"/"), slack.OptionHTTPClient(server.Client()))
	caller := &corrOneShotLLMCaller{respond: func(context.Context) (string, error) {
		return `{"alert_name":"PR change ready for review","summary":"tested on staging","event_kind":"change","event_confidence":0.96,"event_reasoning":"pre-merge change announcement"}`, nil
	}}
	handler := NewSlackHandler(client, nil, nil, nil, caller)
	handler.SetEventService(services.NewEventService(db, caller))
	channel := &database.Channel{UUID: "channel-uuid", ExternalID: "C_CHANGES", CanListen: true, CanPost: false}
	msg := &slackevents.MessageEvent{
		Channel: "C_CHANGES", TimeStamp: "1707000033.001100", User: "U_ENGINEER",
		Text: "Please review and merge https://github.com/example/repo/pull/14 — tested on staging",
	}
	handler.handleAlertChannelMessage(msg, channel)
	var events []database.Event
	if err := db.Find(&events).Error; err != nil {
		t.Fatal(err)
	}
	if len(events) != 1 || events[0].Kind != database.EventKindChange || events[0].SourceKind != database.EventSourceSlackListener {
		t.Fatalf("listener change event not correctly stored: %+v", events)
	}
	var runs []database.AgentRun
	if err := db.Find(&runs).Error; err != nil {
		t.Fatal(err)
	}
	var incidents []database.Incident
	if err := db.Find(&incidents).Error; err != nil {
		t.Fatal(err)
	}
	if len(runs) != 0 || len(incidents) != 0 {
		t.Fatalf("current contract must store only and start no run/incident: runs=%d incidents=%d", len(runs), len(incidents))
	}
	t.Logf("source-native listener change: recorded=%d classified=%s runs=%d incidents=%d", len(events), events[0].Kind, len(runs), len(incidents))
}

// Research-only negative control: invoking the *mention-request* dispatcher
// after a listener change is NOT a safe way to implement issue #79.
// The path classifies again and records a second event under a different source.
// This is a deliberately injected bad integration, not a production invocation.
func TestBatch40NaiveMentionReuseAfterChangeCreatesDuplicateEvent(t *testing.T) {
	db := setupEventsHandlerDB(t)
	if err := db.Create(&database.SlackSettings{
		Enabled: true, BotToken: "test-bot", SigningSecret: "test-secret", AppToken: "test-app",
	}).Error; err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = fmt.Fprint(w, `{"ok":true,"messages":[],"channel":"C_CHANGES","ts":"1707000033.001100"}`)
	}))
	defer server.Close()
	client := slack.New("test-token", slack.OptionAPIURL(server.URL+"/"), slack.OptionHTTPClient(server.Client()))
	var classified int
	caller := &corrOneShotLLMCaller{respond: func(context.Context) (string, error) {
		classified++
		return `{"alert_name":"Review PR change","event_kind":"change","event_confidence":0.99}`, nil
	}}
	handler := NewSlackHandler(client, nil, nil, nil, caller)
	handler.SetEventService(services.NewEventService(db, caller))
	channel := &database.Channel{UUID: "channel-uuid", ExternalID: "C_CHANGES", CanListen: true, CanPost: false}
	msg := &slackevents.MessageEvent{
		Channel: "C_CHANGES", TimeStamp: "1707000033.001100", User: "U_ENGINEER",
		Text: "Review PR https://github.com/example/repo/pull/14",
	}
	handler.handleAlertChannelMessage(msg, channel)
	if classified != 1 {
		t.Fatalf("want 1 initial LLM classification, got %d", classified)
	}
	// The tempting shortcut when adding on_change=run:
	// reuse the human-mention request path for an already-classified listener.
	handler.processMessage(msg.Channel, "", msg.TimeStamp, msg.Text, msg.User)
	var events []database.Event
	if err := db.Find(&events).Error; err != nil {
		t.Fatal(err)
	}
	var runs []database.AgentRun
	if err := db.Find(&runs).Error; err != nil {
		t.Fatal(err)
	}
	if classified != 2 || len(events) != 2 || len(runs) != 0 {
		t.Fatalf("naive re-dispatch: classified=%d events=%d runs=%d; expected 2,2,0", classified, len(events), len(runs))
	}
	if events[0].SourceKind == events[1].SourceKind {
		t.Fatalf("expected two distinct source kinds, got %+v", events)
	}
	t.Logf("naive reuse causes %d classifications and %d stored event sources, still %d agent runs; a preclassified event-to-request route is necessary", classified, len(events), len(runs))
}
