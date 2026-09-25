package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Node struct {
	ID           string
	Type         string
	VectorWeight float64
}

type Hypergraph struct {
	Nodes       map[string]Node `json:"nodes"`
	GoldenPaths map[string]bool `json:"golden_paths"`
	DeadEnds    map[string]bool `json:"dead_ends"`
}

func main() {
	graph := Hypergraph{
		Nodes:       GenNodes,
		GoldenPaths: GenGoldenPaths,
		DeadEnds:    GenDeadEnds,
	}

	data, err := json.MarshalIndent(graph, "", "  ")
	if err != nil {
		fmt.Printf("Error marshaling to JSON: %v\n", err)
		os.Exit(1)
	}

	err = os.WriteFile("hypergraph_dataset.json", data, 0644)
	if err != nil {
		fmt.Printf("Error writing JSON file: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Successfully exported hypergraph_dataset.json")
}
