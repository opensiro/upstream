package services

import (
	"testing"

	"github.com/akmatori/akmatori/internal/database"
)

// Research-only source-native falsifier for batch 40 (#303).
// NOT a change proposed for the original repository.
// A cited memory is NOT an independently corroborated incident conclusion.
func TestBatch40CitedUsageIsNotCrossIncidentCorroboration(t *testing.T) {
	db, memoryService := usageTestDB(t)
	original := database.Memory{
		Scope: "global", Name: "redis-502",
		Type: MemoryTypeFact, Description: "load caused 502",
		Body:         "Hypothesis, not confirmed by an operator",
		IncidentUUID: "inc-A", CreatedBy: MemoryCreatedByAgent,
		Claim: MemoryClaimCausal, Evidence: MemoryEvidenceUnverified,
	}
	if err := db.Create(&original).Error; err != nil {
		t.Fatal(err)
	}
	// Positive control: two independently *identified runs* reference the same memory.
	// Negative control: a second run in inc-B cites it again: use_count inflates,
	// but the number of independent incidents must not increase.
	for _, run := range []struct{ id, incident string }{
		{"run-a", "inc-A"}, {"run-b", "inc-B"}, {"run-b2", "inc-B"},
	} {
		if count := memoryService.RecordCitedMemories(
			run.id, run.incident, "Summary\nMemory used: [[global/redis-502]]",
		); count != 1 {
			t.Fatalf("%s: cited count=%d", run.id, count)
		}
	}
	var after database.Memory
	if err := db.First(&after, original.ID).Error; err != nil {
		t.Fatal(err)
	}
	if after.UseCount != 3 {
		t.Fatalf("unexpected use count %d, want 3", after.UseCount)
	}
	var distinctIncidents int64
	if err := db.Model(&database.MemoryUse{}).
		Where("memory_id = ?", original.ID).
		Distinct("incident_uuid").Count(&distinctIncidents).Error; err != nil {
		t.Fatal(err)
	}
	if distinctIncidents != 2 {
		t.Fatalf("independent incident count %d, want 2", distinctIncidents)
	}
	if after.Evidence != MemoryEvidenceUnverified {
		t.Fatalf("CITATION MUST NOT AUTO-CONFIRM unverified causal memory: %s", after.Evidence)
	}
	// The *same semantic description*, extracted independently for inc-C,
	// can be stored as another unverified memory; no implicit cross-memory merge.
	independent := database.Memory{
		Scope: "global", Name: "redis-502-alt", Type: MemoryTypeFact,
		Description: original.Description, Body: original.Body,
		IncidentUUID: "inc-C", CreatedBy: MemoryCreatedByAgent,
		Claim: MemoryClaimCausal, Evidence: MemoryEvidenceUnverified,
	}
	if err := db.Create(&independent).Error; err != nil {
		t.Fatal(err)
	}
	var found int64
	if err := db.Model(&database.Memory{}).Where("description = ?", original.Description).Count(&found).Error; err != nil {
		t.Fatal(err)
	}
	if found != 2 {
		t.Fatalf("expected two distinct native memories, got %d", found)
	}
	if independent.Evidence != MemoryEvidenceUnverified {
		t.Fatalf("unexpected independent evidence grade %s", independent.Evidence)
	}
}
