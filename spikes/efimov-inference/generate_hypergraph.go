package main

import (
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())

	numNodes := 100000
	chainDepth := 10000 // Test fuel exhaustion

	var out strings.Builder
	out.WriteString("package main\n\n")

	// The struct is defined in main.go, we just populate the map
	out.WriteString("// Auto-generated Hypergraph Data\n")
	out.WriteString("var GenNodes = map[string]Node{\n")

	// 1. Generate base nodes
	nodeIDs := make([]string, 0, numNodes)
	for i := 0; i < numNodes; i++ {
		id := fmt.Sprintf("node_%06d", i)
		nodeIDs = append(nodeIDs, id)
		
		// QW64 complex amplitude simulation: [real, imag] mapped roughly to a single float for the current emulator structure
		// In a true Wyrd struct it would be [2]float64, but we keep it compatible with our existing main.go struct initially
		realPart := rand.Float64()
		out.WriteString(fmt.Sprintf("\t\"%s\": {\"%s\", \"compute\", %.4f},\n", id, id, realPart))
	}
	// ZDCHK Trap Nodes
	out.WriteString("\t\"node_sedenion_zd_1\": {\"node_sedenion_zd_1\", \"compute\", 0.5000},\n")
	out.WriteString("\t\"node_sedenion_zd_2\": {\"node_sedenion_zd_2\", \"compute\", 1.5000},\n")
	out.WriteString("\t\"node_sedenion_zd_3\": {\"node_sedenion_zd_3\", \"compute\", 3.5000},\n")

	// Semantic Singularity Nodes (Thomas Collapse) - Distance < 1e-9
	out.WriteString("\t\"node_collapse_001\": {\"node_collapse_001\", \"compute\", 0.1234567891},\n")
	out.WriteString("\t\"node_collapse_002\": {\"node_collapse_002\", \"compute\", 0.1234567892},\n")
	out.WriteString("\t\"node_collapse_003\": {\"node_collapse_003\", \"compute\", 0.1234567895},\n")

	out.WriteString("}\n\n")

	// 2. Generate Golden Paths (Deep Chains)
	out.WriteString("var GenGoldenPaths = map[string]bool{\n")
	var sequence []string
	
	// Create a single ultra-deep chain with step size 2
	for i := 0; i < chainDepth-2; i += 2 {
		triad := fmt.Sprintf("%s|%s|%s", nodeIDs[i], nodeIDs[i+1], nodeIDs[i+2])
		out.WriteString(fmt.Sprintf("\t\"%s\": true,\n", triad))
		
		// Push sequence for I/O thread
		if i == 0 {
			sequence = append(sequence, nodeIDs[i], nodeIDs[i+1], nodeIDs[i+2])
		} else {
			sequence = append(sequence, nodeIDs[i+1], nodeIDs[i+2])
		}
	}
	
	// 3. Create a Confluence Point
	confluA := fmt.Sprintf("%s|%s|confluence_target", nodeIDs[10], nodeIDs[15])
	confluB := fmt.Sprintf("%s|%s|confluence_target", nodeIDs[20], nodeIDs[25])
	out.WriteString(fmt.Sprintf("\t\"%s\": true,\n", confluA))
	out.WriteString(fmt.Sprintf("\t\"%s\": true,\n", confluB))
	out.WriteString("}\n\n")

	// 4. Generate Dead Ends
	out.WriteString("var GenDeadEnds = map[string]bool{\n")
	out.WriteString(fmt.Sprintf("\t\"%s|%s|dead_end\": true,\n", nodeIDs[5], nodeIDs[6]))
	// We'll also use one of the collision spots as a trigger to flush, but technically Dead Ends just advance RP
	out.WriteString("}\n\n")
	
	// Inject dead end at the start of sequence
	// Also inject ZDCHK sequence, Semantic Singularity sequence, and a branching collision trigger into the main traversal path
	specialSequence := []string{
		"node_collapse_001", "node_collapse_002", "node_collapse_003", // Thomas Collapse
		"node_sedenion_zd_1", "node_sedenion_zd_2", "node_sedenion_zd_3", // ZDCHK trap
		nodeIDs[5], nodeIDs[6], "dead_end", // Normal dead end
		"node_drift_seam", "node_dummy_1", "node_dummy_2", // Branching collision
	}
	finalSequence := append(specialSequence, sequence...)

	out.WriteString("var GenSequence = []string{\n")
	for _, id := range finalSequence {
		out.WriteString(fmt.Sprintf("\t\"%s\",\n", id))
	}
	out.WriteString("}\n")

	err := os.WriteFile("hypergraph_data.go", []byte(out.String()), 0644)
	if err != nil {
		fmt.Printf("Error writing file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Successfully generated hypergraph_data.go with %d nodes and a chain depth of %d.\n", numNodes, chainDepth)
}
