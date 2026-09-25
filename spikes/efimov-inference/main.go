package main

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
)

// Hypergraph node
type Node struct {
	ID           string
	Type         string
	VectorWeight float64
}

// Auto-generated variables from hypergraph_data.go:
// GenNodes, GenGoldenPaths, GenDeadEnds, GenSequence

// THEATER: ZDCHKLUT (one hardcoded key) is a stub, not an actual mitigation.
var ZDCHKLUT = map[string]bool{
	"node_sedenion_zd_1|node_sedenion_zd_2|node_sedenion_zd_3": true,
}

const BufferSize = 4

type RingBuffer struct {
	nodes [BufferSize]string
	wp    uint64
	rp    uint64
	mu    sync.Mutex
	cond  *sync.Cond
}

func NewRingBuffer() *RingBuffer {
	rb := &RingBuffer{}
	rb.cond = sync.NewCond(&rb.mu)
	return rb
}

func (rb *RingBuffer) Write(node string) {
	rb.mu.Lock()
	defer rb.mu.Unlock()
	for rb.wp-rb.rp == BufferSize {
		// Buffer full, stall I/O thread
		rb.cond.Wait()
	}
	idx := rb.wp % BufferSize
	_ = rb.nodes[idx]
	rb.nodes[idx] = node
	// fmt.Printf("[I/O Thread] Wrote '%s' to buffer[%d] (WP=%d)", node, idx, rb.wp)
	// if old != "" {
	// 	fmt.Printf(" silently overwriting '%s'", old)
	// }
	// fmt.Println()
	rb.wp++
	rb.cond.Broadcast()
}

func (rb *RingBuffer) ReadTriad() (string, string, string, uint64) {
	rb.mu.Lock()
	defer rb.mu.Unlock()
	for rb.wp-rb.rp < 3 {
		// Buffer starved, stall compute thread
		rb.cond.Wait()
	}
	n1 := rb.nodes[rb.rp%BufferSize]
	n2 := rb.nodes[(rb.rp+1)%BufferSize]
	n3 := rb.nodes[(rb.rp+2)%BufferSize]
	return n1, n2, n3, rb.rp
}

func (rb *RingBuffer) AdvanceReadPointer(amount uint64) {
	rb.mu.Lock()
	defer rb.mu.Unlock()
	rb.rp += amount
	rb.cond.Broadcast()
}

func (rb *RingBuffer) Flush(anchor uint64) {
	rb.mu.Lock()
	defer rb.mu.Unlock()
	fmt.Printf("[Wyrd Engine] Branching collision detected. RingBuffer Flush() called. Re-anchoring to RP=%d\n", anchor)
	rb.wp = anchor
	rb.rp = anchor
	rb.cond.Broadcast()
}

func runSpike(fuelBudget int) {
	fmt.Printf("\n=== Starting Wyrd/Edda Spike (Fuel Budget: %d) ===\n", fuelBudget)
	rb := NewRingBuffer()
	
	var wg sync.WaitGroup
	wg.Add(2)
	
	// Fuel counter
	var fuel int32 = int32(fuelBudget)
	var targetReached int32 = 0
	
	// I/O Thread (Stepped Leader & Edda Compiler Pre-processing)
	go func() {
		defer wg.Done()
		
		sequence := GenSequence
		
		// AST Pre-processing for Thomas Collapse
		var collapsedSequence []string
		const epsilon = 1e-9
		for i := 0; i < len(sequence); i++ {
			node1 := sequence[i]
			if i < len(sequence)-1 {
				node2 := sequence[i+1]
				n1Data, ok1 := GenNodes[node1]
				n2Data, ok2 := GenNodes[node2]
				if ok1 && ok2 {
					// THEATER: "Thomas Collapse" (math.Abs merge) is a stub, not a real mitigation.
					dist := math.Abs(n1Data.VectorWeight - n2Data.VectorWeight)
					if dist < epsilon {
						fmt.Printf("[Edda Compiler] Thomas Collapse: merged %s and %s (dist=%.2e) into NT_SCOPE_CONCEPTUAL\n", node1, node2, dist)
						// Skip node2 by continuing, node1 stays as the super-node
						continue
					}
				}
			}
			collapsedSequence = append(collapsedSequence, node1)
		}
		
		for _, node := range collapsedSequence {
			if atomic.LoadInt32(&fuel) <= 0 || atomic.LoadInt32(&targetReached) == 1 {
				return
			}
			if node == "node_drift_seam" {
				// Simulate I/O thread stalling on full buffer during drift seam enqueue
				rb.Flush(rb.rp)
			}
			rb.Write(node)
		}
	}()
	
	// Compute Thread (Trailing execution)
	go func() {
		defer wg.Done()
		
		for {
			if atomic.LoadInt32(&fuel) <= 0 {
				fmt.Printf("[Compute Thread] HALT: Fuel budget depleted (Deterministic Failure).\n")
				return
			}
			if atomic.LoadInt32(&targetReached) == 1 {
				return
			}
			
			n1, n2, n3, _ := rb.ReadTriad()
			triadKey := fmt.Sprintf("%s|%s|%s", n1, n2, n3)
			
			// Evaluate Efimov geometry
			// fmt.Printf("[Compute Thread] Evaluating Efimov triad: [%s, %s, %s] at RP=%d\n", n1, n2, n3, currentRp)
			
			if GenDeadEnds[triadKey] {
				atomic.AddInt32(&fuel, -1)
				// Reject the entire triad, advance RP by 3 to clear the buffer
				rb.AdvanceReadPointer(3)
			} else if ZDCHKLUT[triadKey] {
				atomic.AddInt32(&fuel, -1)
				// THEATER: The [Gearbox] print is a stub.
				fmt.Printf("[Gearbox] ZDCHK trap hit for %s. Emitting TOKEN_DEGENERATE_RESONANCE.\n", triadKey)
				// Bridge the gap successfully instead of failing
				rb.AdvanceReadPointer(2)
			} else if GenGoldenPaths[triadKey] {
				atomic.AddInt32(&fuel, -1)
				
				if n3 == GenSequence[len(GenSequence)-1] {
					fmt.Printf("   -> TARGET REACHED: %s\n", n3)
					atomic.StoreInt32(&targetReached, 1)
					
					// Capability Hash Chain (Cliff 4)
					hasher := sha256.New()
					hasher.Write([]byte("scope_physics"))
					hasher.Write([]byte(triadKey))
					hasher.Write([]byte("scope_biology"))
					chainHash := hasher.Sum(nil)
					
					// Mint ED25519 signature wrapping the hash chain
					// THEATER: ephemeral self-signed key is a stub, not a mitigation (not wired to Contextus/BMA).
					// The "trusted NT_INSIGHT_SIGNAL" is just a self-signed ephemeral key, not actual trust.
					pub, priv, _ := ed25519.GenerateKey(nil)
					sig := ed25519.Sign(priv, chainHash)
					fmt.Printf("\n[Edda Compiler] Invariant locked. Minted NT_INSIGHT_SIGNAL with Capability Hash Chain:\n")
					fmt.Printf("Chain Hash: %s\n", hex.EncodeToString(chainHash))
					fmt.Printf("PubKey: %s\n", hex.EncodeToString(pub))
					fmt.Printf("Signature: %s\n", hex.EncodeToString(sig))
					
					return
				}
				
				// Advance RP by 2 so the last node becomes the first node of the next triad
				rb.AdvanceReadPointer(2)
			} else {
				// Should not happen with our hardcoded stream, but acts as a fallback
				fmt.Printf("   -> UNKNOWN PATH. Stalling or ignoring.\n")
				rb.AdvanceReadPointer(1)
			}
		}
	}()
	
	wg.Wait()
	if atomic.LoadInt32(&targetReached) == 1 {
		fmt.Println("=== Spike Completed Successfully ===")
	} else {
		fmt.Println("=== Spike Terminated (Out of Fuel) ===")
	}
}

func main() {
	// Run 1: Successful Execution
	runSpike(15000)
	
	// Run 2: Deterministic Failure (insufficient fuel for a deep chain)
	runSpike(4998)
}
