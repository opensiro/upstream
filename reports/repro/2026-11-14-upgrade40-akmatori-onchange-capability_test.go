package handlers

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"regexp"
	"testing"

	"github.com/akmatori/akmatori/internal/database"
	"github.com/akmatori/akmatori/internal/services"
	"github.com/slack-go/slack"
	"github.com/slack-go/slack/slackevents"
	"gorm.io/gorm"
)

// Research-only adapter SPECIMEN, not a feature in Akmatori. The original
// handler still has no on_change mode. This adapter uses existing first-party
// EventService + AgentRun tables to test a bounded positive capability proxy.
// It does NOT dispatch a worker or post to a real Slack thread.
type batch40ResearchChangePolicy struct {
	OnChange                    string // store is the current default; run is only a proposed mode.
	Enabled, CanListen, CanPost bool
	Filter                      string
	RootSkill                   string
}

func batch40ResearchPreclassifiedRun(db *gorm.DB, ev database.Event, channel *database.Channel, originalText, threadTS string, p batch40ResearchChangePolicy) (string, error) {
	if p.OnChange != "run" {
		return "", nil
	}
	if !p.Enabled || !p.CanListen || !p.CanPost {
		return "", nil
	}
	if p.RootSkill != "incident-manager" {
		return "", nil
	} // no implicit new skill authority
	if ev.Kind != database.EventKindChange || ev.SourceKind != database.EventSourceSlackListener || ev.UUID == "" ||
		ev.SourceUUID != channel.UUID || ev.ExternalID != threadTS || channel.ExternalID == "" {
		return "", nil
	}
	if p.Filter != "" {
		rx, err := regexp.Compile(p.Filter)
		if err != nil {
			return "", nil
		} // invalid filter fails closed
		if !rx.MatchString(originalText) {
			return "", nil
		}
	}
	var n int64
	if err := db.Model(&database.AgentRun{}).Where("event_uuid = ?", ev.UUID).Count(&n).Error; err != nil {
		return "", err
	}
	if n != 0 {
		return "", nil
	} // serial replay only; NOT concurrent atomic admission
	run := &database.AgentRun{
		ScopeUUID: ev.UUID, EventUUID: ev.UUID, IncidentUUID: "",
		SourceKind: database.EventSourceSlackListener, SourceUUID: ev.SourceUUID,
		RootSkill: "incident-manager", SlackChannelID: channel.ExternalID, SlackThreadTS: threadTS,
	}
	if err := database.BeginAgentRun(db, run); err != nil {
		return "", err
	}
	if err := db.Model(&database.Event{}).Where("uuid = ?", ev.UUID).Update("scope_uuid", ev.UUID).Error; err != nil {
		return "", err
	}
	return run.RunID, nil
}
func TestBatch40CapabilityFirstChangeRunResearchControls(t *testing.T) {
	cases := []struct {
		name, classifiedKind, mode, filter, rootSkill string
		enabled, listen, post                         bool
		expected                                      int
	}{
		{"default_store_compatibility", "change", "store", "", "incident-manager", true, true, true, 0},
		{"explicit_opt_in_run", "change", "run", "https://github\\.com/[^ ]+/pull/[0-9]+", "incident-manager", true, true, true, 1},
		{"info_remains_store_only", "info", "run", "", "incident-manager", true, true, true, 0},
		{"disabled_channel", "change", "run", "", "incident-manager", false, true, true, 0},
		{"non_listening_channel", "change", "run", "", "incident-manager", true, false, true, 0},
		{"cannot_reply_to_thread", "change", "run", "", "incident-manager", true, true, false, 0},
		{"filter_miss", "change", "run", "completely-unrelated", "incident-manager", true, true, true, 0},
		{"invalid_filter_fails_closed", "change", "run", "[", "incident-manager", true, true, true, 0},
		{"unsupported_skill_fails_closed", "change", "run", "", "arbitrary-privileged-skill", true, true, true, 0},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db := setupEventsHandlerDB(t)
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
				w.Header().Set("Content-Type", "application/json")
				_, _ = fmt.Fprint(w, `{"ok":true,"messages":[]}`)
			}))
			defer server.Close()
			client := slack.New("test-token", slack.OptionAPIURL(server.URL+"/"), slack.OptionHTTPClient(server.Client()))
			count := 0
			caller := &corrOneShotLLMCaller{respond: func(context.Context) (string, error) {
				count++
				return fmt.Sprintf(`{"alert_name":"pre-merge review","event_kind":%q,"event_confidence":0.95}`, tc.classifiedKind), nil
			}}
			h := NewSlackHandler(client, nil, nil, nil, caller)
			h.SetEventService(services.NewEventService(db, caller))
			ch := &database.Channel{UUID: "channel-uuid", ExternalID: "C_CHANGES", CanListen: true, CanPost: true}
			msg := &slackevents.MessageEvent{Channel: ch.ExternalID, TimeStamp: "1707000042.000100", User: "U_ENGINEER", Text: "Please review https://github.com/example/repo/pull/14 before merge"}
			h.handleAlertChannelMessage(msg, ch)
			var events []database.Event
			if err := db.Find(&events).Error; err != nil {
				t.Fatal(err)
			}
			if len(events) != 1 || count != 1 {
				t.Fatalf("original handler must make one event, one classification, got events=%d calls=%d", len(events), count)
			}
			runID, err := batch40ResearchPreclassifiedRun(db, events[0], ch, msg.Text, msg.TimeStamp, batch40ResearchChangePolicy{
				OnChange: tc.mode, Enabled: tc.enabled, CanListen: tc.listen, CanPost: tc.post, Filter: tc.filter, RootSkill: tc.rootSkill,
			})
			if err != nil {
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
			if len(runs) != tc.expected || len(incidents) != 0 || count != 1 || len(events) != 1 {
				t.Fatalf("research adapter: events=%d classifications=%d runs=%d want=%d incidents=%d", len(events), count, len(runs), tc.expected, len(incidents))
			}
			if tc.expected == 1 {
				if runID == "" || runs[0].EventUUID != events[0].UUID || runs[0].ScopeUUID != events[0].UUID ||
					runs[0].IncidentUUID != "" || runs[0].SlackThreadTS != msg.TimeStamp || runs[0].SlackChannelID != ch.ExternalID ||
					runs[0].SourceKind != database.EventSourceSlackListener {
					t.Fatalf("run provenance wrong %+v event=%+v", runs[0], events[0])
				}
				work, err := lookupSlackThread(msg.TimeStamp)
				if err != nil || work.ScopeUUID != events[0].UUID || work.IncidentUUID != "" {
					t.Fatalf("native thread lookup failed: work=%+v err=%v", work, err)
				}
				_, err = batch40ResearchPreclassifiedRun(db, events[0], ch, msg.Text, msg.TimeStamp, batch40ResearchChangePolicy{
					OnChange: tc.mode, Enabled: tc.enabled, CanListen: tc.listen, CanPost: tc.post, Filter: tc.filter, RootSkill: tc.rootSkill,
				})
				if err != nil {
					t.Fatal(err)
				}
				var retryCount int64
				if err := db.Model(&database.AgentRun{}).Where("event_uuid = ?", events[0].UUID).Count(&retryCount).Error; err != nil {
					t.Fatal(err)
				}
				if retryCount != 1 {
					t.Fatalf("serial replay produced %d runs", retryCount)
				}
				if err := database.FinishAgentRun(db, runID, database.AgentRunResult{
					Response: "Review ready: check risk, test evidence and rollback; no merge executed", SessionID: "research-worker-fixture",
				}); err != nil {
					t.Fatal(err)
				}
				work, err = lookupSlackThread(msg.TimeStamp)
				if err != nil || work.Response == "" {
					t.Fatalf("completed research-worker response not visible in first-party threaded lookup: work=%+v err=%v", work, err)
				}
			} else if runID != "" {
				t.Fatalf("no-run case returned run ID %s", runID)
			}
			t.Logf("mode=%s original_event=%s original_kind=%s classifier_calls=%d agent_run_rows=%d incidents=%d", tc.mode, events[0].UUID, events[0].Kind, count, len(runs), len(incidents))
		})
	}
}
