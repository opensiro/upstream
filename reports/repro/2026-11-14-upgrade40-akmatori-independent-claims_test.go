package services

import (
	"testing"

	"github.com/akmatori/akmatori/internal/database"
)

// Research-only source-native revisit of Akmatori's first-party applyExtractedMemory.
// Run in a disposable pinned checkout, never in original repo.
func TestBatch40IndependentIncidentClaimsAndContradictionRemainSeparate(t *testing.T) {
	db, _ := usageTestDB(t)
	confirmed := database.Memory{
		Scope: "global", Name: "redis-failures", Type: MemoryTypeFact,
		Description: "Operator-confirmed DNS issue", Body: "Operator checked",
		IncidentUUID: "inc-operator", CreatedBy: "operator",
		Claim: MemoryClaimCausal, Evidence: MemoryEvidenceConfirmed,
	}
	if err := db.Create(&confirmed).Error; err != nil {
		t.Fatal(err)
	}

	insert := func(incident, description string) database.Memory {
		t.Helper()
		m := database.Memory{
			Scope: "global", Name: "redis-failures", Type: MemoryTypeFact,
			Description: description, Body: description, IncidentUUID: incident,
			CreatedBy: MemoryCreatedByAgent, Claim: MemoryClaimCausal,
			Evidence: MemoryEvidenceObserved, // malicious/overconfident draft
		}
		if _, err := ApplyAgentMemoryEvidence(&m); err != nil {
			t.Fatal(err)
		}
		if m.Evidence != MemoryEvidenceUnverified {
			t.Fatalf("agent causal memory must not be observed or confirmed: %#v", m)
		}
		if err := applyExtractedMemory(db, &m); err != nil {
			t.Fatal(err)
		}
		return m
	}
	a := insert("inc-A", "Redis caused repeated 502 errors")
	b := insert("inc-B", "Redis caused repeated 502 errors")
	opposite := insert("inc-C", "Reverse proxy caused repeated 502 errors")
	if a.Name != "redis-failures-2" || b.Name != "redis-failures-3" || opposite.Name != "redis-failures-4" {
		t.Fatalf("claims not separately named: %s %s %s", a.Name, b.Name, opposite.Name)
	}
	// Same incident re-extraction is a semantic UPDATE, not a new independent incident.
	newB := insert("inc-B", "Redis caused repeated 502 errors after retry")
	if newB.ID != b.ID || newB.Name != b.Name {
		t.Fatalf("rerun lost stable ownership: before %#v after %#v", b, newB)
	}
	var memories []database.Memory
	if err := db.Order("name").Find(&memories).Error; err != nil {
		t.Fatal(err)
	}
	if len(memories) != 4 {
		t.Fatalf("want one confirmed operator + three separate unverified incident claims, got %d", len(memories))
	}
	for _, m := range memories {
		if m.IncidentUUID == "inc-operator" {
			if m.Evidence != MemoryEvidenceConfirmed || m.Description != confirmed.Description {
				t.Fatalf("agent overwrote operator record: %#v", m)
			}
		} else if m.Evidence != MemoryEvidenceUnverified {
			t.Fatalf("unconfirmed incident claim was automatically promoted: %#v", m)
		}
	}
	t.Logf("separate_claims=%d operator_confirmed=1 agent_unverified=3 rerun_same_incident_updates_in_place=true contradictory_claim_is_not_cross_checked=true", len(memories))
}
