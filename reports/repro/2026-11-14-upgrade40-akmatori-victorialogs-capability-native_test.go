package victoriametrics

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

// Research-only VictoriaLogs LogsQL fixture, NOT a shipping tool type or
// source extension. Akmatori #48 requests real VictoriaLogs logs during triage.
type batch40VLConfig struct {
	URL, Auth, Token, Username, Password, Header, HeaderValue string
}
type batch40VLRecord struct {
	Time    string `json:"_time"`
	Host    string `json:"host"`
	Message string `json:"_msg"`
}

func batch40VLQuery(ctx context.Context, cfg batch40VLConfig, q, start, end string, limit int) ([]batch40VLRecord, error) {
	if cfg.URL == "" || q == "" {
		return nil, fmt.Errorf("missing VictoriaLogs URL or LogsQL query")
	}
	a, err := time.Parse(time.RFC3339, start)
	if err != nil {
		return nil, fmt.Errorf("invalid start: %w", err)
	}
	b, err := time.Parse(time.RFC3339, end)
	if err != nil {
		return nil, fmt.Errorf("invalid end: %w", err)
	}
	if !b.After(a) || b.Sub(a) > 6*time.Hour {
		return nil, fmt.Errorf("outside bounded time range")
	}
	if limit == 0 {
		limit = 50
	}
	if limit < 1 || limit > 200 {
		return nil, fmt.Errorf("invalid output line limit")
	}
	base, err := url.Parse(cfg.URL)
	if err != nil || base.Scheme == "" || base.Host == "" || base.User != nil || base.RawQuery != "" || base.Fragment != "" {
		return nil, fmt.Errorf("invalid vl_url")
	}
	if base.Scheme != "http" && base.Scheme != "https" {
		return nil, fmt.Errorf("invalid URL scheme")
	}
	if base.Path != "" && base.Path != "/" {
		return nil, fmt.Errorf("path in vl_url forbidden in fixture")
	}
	base.Path = "/select/logsql/query"
	form := url.Values{"query": {q}, "start": {start}, "end": {end}, "limit": {fmt.Sprintf("%d", limit)}}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, base.String(), strings.NewReader(form.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	switch cfg.Auth {
	case "none":
	case "bearer":
		if cfg.Token == "" {
			return nil, fmt.Errorf("missing bearer token")
		}
		req.Header.Set("Authorization", "Bearer "+cfg.Token)
	case "basic":
		if cfg.Username == "" {
			return nil, fmt.Errorf("missing basic username")
		}
		req.SetBasicAuth(cfg.Username, cfg.Password)
	case "header":
		if cfg.Header == "" || cfg.HeaderValue == "" || !strings.HasPrefix(strings.ToLower(cfg.Header), "x-") {
			return nil, fmt.Errorf("custom header only with explicit x-* name/value in research fixture")
		}
		req.Header.Set(cfg.Header, cfg.HeaderValue)
	default:
		return nil, fmt.Errorf("unknown auth mode")
	}
	client := &http.Client{Timeout: 2 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("VictoriaLogs HTTP status %d", resp.StatusCode)
	}
	// Bounded response bytes. VictoriaLogs query responses are line-wise JSON;
	// this is NOT VictoriaMetrics's Prometheus JSON envelope.
	const maxBytes = 128 * 1024
	body, err := io.ReadAll(io.LimitReader(resp.Body, maxBytes+1))
	if err != nil {
		return nil, err
	}
	if len(body) > maxBytes {
		return nil, fmt.Errorf("VictoriaLogs response too large")
	}
	sc := bufio.NewScanner(strings.NewReader(string(body)))
	sc.Buffer(make([]byte, 1024), maxBytes)
	out := make([]batch40VLRecord, 0, limit)
	for sc.Scan() {
		if len(out) >= limit {
			return nil, fmt.Errorf("VictoriaLogs server exceeded output record limit")
		}
		var rec batch40VLRecord
		if err := json.Unmarshal(sc.Bytes(), &rec); err != nil {
			return nil, fmt.Errorf("invalid NDJSON: %w", err)
		}
		if rec.Time == "" || rec.Message == "" {
			return nil, fmt.Errorf("missing required VictoriaLogs fields")
		}
		out = append(out, rec)
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	return out, nil
}

func TestBatch40VictoriaLogsNewTriageWorkflowAndOriginalBoundary(t *testing.T) {
	var originalQueries, newQueries atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/api/v1/query":
			originalQueries.Add(1)
			w.Header().Set("Content-Type", "application/json")
			_, _ = fmt.Fprint(w, `{"status":"success","data":{"resultType":"vector","result":[{"metric":{"job":"myservice"},"value":[1794684600,"1"]}]}}`)
		case "/select/logsql/query":
			newQueries.Add(1)
			_ = r.ParseForm()
			if r.Method != http.MethodPost || r.FormValue("query") != "myservice" || r.FormValue("limit") != "3" ||
				r.FormValue("start") != "2026-11-14T18:00:00Z" || r.FormValue("end") != "2026-11-14T20:00:00Z" {
				t.Errorf("bad LogsQL request: method=%s path=%s form=%v", r.Method, r.URL.Path, r.Form)
			}
			if r.Header.Get("Authorization") != "Bearer testing-token" {
				t.Errorf("missing credentials in bounded request")
			}
			w.Header().Set("Content-Type", "application/stream+json")
			_, _ = fmt.Fprint(w, `{"_time":"2026-11-14T19:00:00Z","host":"node-a","_msg":"systemd myservice crash loop: exit code 1"}
{"_time":"2026-11-14T19:01:00Z","host":"node-a","_msg":"systemd restarted myservice after failure"}
`)
		default:
			t.Errorf("unexpected endpoint %s", r.URL.Path)
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer server.Close()
	// Real first-party VictoriaMetrics tool, configured as in its own native
	// tests, intentionally proves that the LogsQL endpoint is not registered.
	tool := NewVictoriaMetricsTool(testLogger(), nil)
	tool.configCache.Set(configCacheKey("test-incident"), &VMConfig{URL: server.URL, AuthMethod: "none", VerifySSL: true, Timeout: 3})
	defer tool.Stop()
	prior, err := tool.InstantQuery(context.Background(), "test-incident", map[string]interface{}{"query": "up{job=\"myservice\"}"})
	if err != nil || !strings.Contains(prior, "resultType") {
		t.Fatalf("current PromQL native path: %q err=%v", prior, err)
	}
	_, err = tool.APIRequest(context.Background(), "test-incident", map[string]interface{}{"path": "/select/logsql/query", "method": "POST", "params": map[string]interface{}{"query": "myservice"}})
	if err == nil || !strings.Contains(err.Error(), "read-only endpoints only") {
		t.Fatalf("existing path unexpectedly handles LogsQL: err=%v", err)
	}
	rows, err := batch40VLQuery(context.Background(), batch40VLConfig{
		URL: server.URL, Auth: "bearer", Token: "testing-token",
	}, "myservice", "2026-11-14T18:00:00Z", "2026-11-14T20:00:00Z", 3)
	if err != nil {
		t.Fatal(err)
	}
	if originalQueries.Load() != 1 || newQueries.Load() != 1 || len(rows) != 2 || rows[0].Host != "node-a" ||
		!strings.Contains(rows[0].Message, "crash loop") || !strings.Contains(rows[1].Message, "restarted") {
		t.Fatalf("new source-backed triage evidence not available: metrics=%d logs=%d records=%+v", originalQueries.Load(), newQueries.Load(), rows)
	}
	t.Logf("first-party PromQL job-health vector returned; LogsQL endpoint refused by original API; source-native research adapter returned %d journal rows exposing a crash loop", len(rows))
}

func TestBatch40VictoriaLogsQuerySafetyAndBounds(t *testing.T) {
	var requests int
	large := strings.Repeat("a", 129*1024)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requests++
		switch r.FormValue("query") {
		case "bad_ndjson":
			_, _ = fmt.Fprint(w, "{bad")
		case "large":
			_, _ = fmt.Fprint(w, large)
		case "more_than_limit":
			_, _ = fmt.Fprint(w, `{"_time":"2026-11-14T19:00:00Z","_msg":"one"}
{"_time":"2026-11-14T19:00:01Z","_msg":"two"}
`)
		default:
			_, _ = fmt.Fprint(w, `{"_time":"2026-11-14T19:00:00Z","_msg":"ok"}`)
		}
	}))
	defer server.Close()
	good := batch40VLConfig{URL: server.URL, Auth: "none"}
	start, end := "2026-11-14T18:00:00Z", "2026-11-14T20:00:00Z"
	for _, tc := range []struct {
		name          string
		cfg           batch40VLConfig
		q, start, end string
		limit         int
	}{
		{"invalid_range", good, "x", end, start, 5},
		{"unbounded_window", good, "x", "2026-11-10T18:00:00Z", end, 5},
		{"invalid_timestamp", good, "x", "not-a-time", end, 5},
		{"invalid_limit", good, "x", start, end, 201},
		{"missing_auth", batch40VLConfig{URL: server.URL, Auth: "bearer"}, "x", start, end, 5},
		{"missing_query", good, "", start, end, 5},
		{"dangerous_base_path", batch40VLConfig{URL: server.URL + "/admin", Auth: "none"}, "x", start, end, 5},
		{"bad_ndjson", good, "bad_ndjson", start, end, 5},
		{"too_large", good, "large", start, end, 5},
		{"exceeds_line_limit", good, "more_than_limit", start, end, 1},
	} {
		t.Run(tc.name, func(t *testing.T) {
			_, err := batch40VLQuery(context.Background(), tc.cfg, tc.q, tc.start, tc.end, tc.limit)
			if err == nil {
				t.Fatal("unsafe or malformed request accepted")
			}
		})
	}
	if requests != 3 {
		t.Fatalf("only three valid-bounded network probes should have been sent, got %d", requests)
	}
	t.Log("bounded LogsQL controls: rejected invalid time, >6h, missing credentials, nonallowed URL, oversized output, invalid NDJSON, over-limit rows")
}

// Config authentication is separate from VictoriaMetrics credential storage.
// This is an HTTP contract fixture only, not a fully approved connector or a
// production credential-resolution test.
func TestBatch40VictoriaLogsAuthModesAndHTTPFailure(t *testing.T) {
	received := make(chan string, 4)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r.ParseForm()
		received <- r.Header.Get("Authorization") + "|" + r.Header.Get("X-Research-Token")
		if r.FormValue("query") == "server_error" {
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		_, _ = fmt.Fprint(w, `{"_time":"2026-11-14T19:00:00Z","host":"host-a","_msg":"service restarted"}`+`
`)
	}))
	defer server.Close()
	start, end := "2026-11-14T18:00:00Z", "2026-11-14T20:00:00Z"
	cases := []struct {
		name   string
		cfg    batch40VLConfig
		wanted string
	}{
		{"none", batch40VLConfig{URL: server.URL, Auth: "none"}, "|"},
		{"basic", batch40VLConfig{URL: server.URL, Auth: "basic", Username: "tester", Password: "pw"}, "Basic dGVzdGVyOnB3|"},
		{"custom_header", batch40VLConfig{URL: server.URL, Auth: "header", Header: "X-Research-Token", HeaderValue: "research-demo"}, "|research-demo"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			rows, err := batch40VLQuery(context.Background(), tc.cfg, "restarts", start, end, 2)
			if err != nil || len(rows) != 1 {
				t.Fatalf("read-only LogsQL query result: %v rows=%+v", err, rows)
			}
			if got := <-received; got != tc.wanted {
				t.Fatalf("credentials passed incorrectly: %q want %q", got, tc.wanted)
			}
		})
	}
	_, err := batch40VLQuery(context.Background(), cases[0].cfg, "server_error", start, end, 2)
	if err == nil || !strings.Contains(err.Error(), "502") {
		t.Fatalf("HTTP 502 must remain an explicit error: %v", err)
	}
	t.Log("three bounded offline auth modes validated; non-success HTTP status was not parsed as log evidence")
}
