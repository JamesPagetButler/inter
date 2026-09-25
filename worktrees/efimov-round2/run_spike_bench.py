import os
import subprocess
import random
import time
import math
import re

def generate_contract(N, filename, nodes):
    lines = []
    lines.append("module efimov.spike")
    lines.append("")
    lines.append(f"contract efimov_scaling_{N} {{")
    lines.append("    tier: C")
    lines.append("    requires: cap(detector_read, scope = screen.locale)")
    lines.append("    body: {")
    
    for i in range(N):
        r, im = nodes[i]
        lines.append(f"        val node{i} : Amplitude[C] @ QW64 = ({r:.6f}, {im:.6f})")
    
    lines.append("")
    
    if N > 1:
        lines.append(f"        val triad1 : Amplitude[C] @ QW64 = node0 * node1")
        for i in range(2, N):
            lines.append(f"        val triad{i} : Amplitude[C] @ QW64 = triad{i-1} * node{i}")
            
    lines.append("    }")
    lines.append("}")
    
    with open(filename, "w") as f:
        f.write("\n".join(lines) + "\n")

def run_codegen(filename, output_dir):
    edda_bin = "/tmp/edda-stage-0"
    cmd = [edda_bin, "build", "--core", filename]
    t0 = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        t1 = time.perf_counter()
        out_file = os.path.join(output_dir, filename.replace(".edda", ".go"))
        with open(out_file, "w") as f:
            f.write(result.stdout)
        return True, t1 - t0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        t1 = time.perf_counter()
        return False, t1 - t0, e.stdout, e.stderr

def postprocess_emulator_go(N, go_file):
    with open(go_file, "r") as f:
        content = f.read()
    
    content = content.replace("package main", "package benchmark")
    content = content.replace("func main() {", f"func RunEmulator(g *emulator.Gearbox) [2]float64 {{")
    if N > 1:
        content = re.sub(r'fmt\.Println\(v_triad\d+\)', f'return v_triad{N-1}', content)
    else:
        content = re.sub(r'fmt\.Println\(v_node0\)', f'return v_node0', content)
    
    # Need to remove the `g := emulator.NewGearbox()` line and `_ = g` if they are created in RunEmulator,
    # because g is passed as a parameter!
    content = content.replace("g := emulator.NewGearbox()", "")
    content = re.sub(r'import\s*\(\s*"fmt"\s*\n\s*"github\.com/JamesPagetButler/qbp-compute-unit/emulator"\s*\)', 'import (\n\t"github.com/JamesPagetButler/qbp-compute-unit/emulator"\n)', content)
    content = re.sub(r'import\s+"fmt"\s*\n', '', content)
    
    with open(go_file, "w") as f:
        f.write(content)

def generate_native(N, filename, nodes):
    lines = []
    lines.append("package benchmark")
    for i in range(N):
        r, im = nodes[i]
        lines.append(f"var N_node{i} = complex({r:.6f}, {im:.6f})")
    lines.append("//go:noinline")
    lines.append("func RunNative() complex128 {")
    if N > 1:
        lines.append(f"    v_triad1 := N_node0 * N_node1")
        for i in range(2, N):
            lines.append(f"    v_triad{i} := v_triad{i-1} * N_node{i}")
        lines.append(f"    res := v_triad{N-1}")
        lines.append("    return res")
    else:
        lines.append("    res := N_node0")
        lines.append("    return res")
    lines.append("}")
    
    with open(filename, "w") as f:
        f.write("\n".join(lines) + "\n")

def generate_benchmark_test(N, filename):
    content = f"""package benchmark
import (
    "testing"
    "github.com/JamesPagetButler/qbp-compute-unit/emulator"
)

var GlobalResEmu [2]float64
func BenchmarkEmulator(b *testing.B) {{
    g := emulator.NewGearbox()
    var res [2]float64
    for i := 0; i < b.N; i++ {{
        res = RunEmulator(g)
    }}
    GlobalResEmu = res
}}

var GlobalResNative complex128
func BenchmarkNative(b *testing.B) {{
    var res complex128
    for i := 0; i < b.N; i++ {{
        res = RunNative()
    }}
    GlobalResNative = res
}}
"""
    with open(filename, "w") as f:
        f.write(content)

def run_benchmarks():
    cmd = ["go", "test", "-vet=off", "-bench", ".", "-benchmem"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stdout + "\n" + e.stderr

def parse_benchmark_ns(stdout):
    emu_ns = 0
    nat_ns = 0
    for line in stdout.split('\n'):
        if "BenchmarkEmulator" in line:
            parts = line.split()
            if len(parts) >= 3:
                emu_ns = float(parts[2])
        if "BenchmarkNative" in line:
            parts = line.split()
            if len(parts) >= 3:
                nat_ns = float(parts[2])
    return emu_ns, nat_ns

def main():
    scales = [3, 10, 100, 1000, 5000, 10000, 100000]
    
    os.makedirs("codegen_bench", exist_ok=True)
    os.chdir("codegen_bench")
    
    random.seed(42)
    
    print("| N | codegen ok? | bench ok? | codegen time | file size (bytes) | emulator (ns/op) | native (ns/op) | overhead × |")
    print("|---|---|---|---|---|---|---|---|")
    
    for N in scales:
        # clear previous files
        for f in os.listdir("."):
            if f.endswith(".go") or f.endswith(".edda") or f == "go.mod" or f == "go.sum":
                os.remove(f)

        subprocess.run(["go", "mod", "init", "benchmark"], capture_output=True)
        subprocess.run(["go", "mod", "edit", "-require", "github.com/JamesPagetButler/qbp-compute-unit/emulator@v0.0.0"], capture_output=True)
        subprocess.run(["go", "mod", "edit", "-replace", "github.com/JamesPagetButler/qbp-compute-unit/emulator=/home/prime/Documents/QBP-Compute-Unit/emulator"], capture_output=True)
        
        nodes = []
        for i in range(N):
            theta = random.uniform(0, 2 * math.pi)
            r = math.cos(theta)
            im = math.sin(theta)
            nodes.append((r, im))
            
        edda_file = f"efimov_scaling_{N}.edda"
        generate_contract(N, edda_file, nodes)
        
        # Codegen
        cg_ok, cg_time, cg_out, cg_err = run_codegen(edda_file, ".")
        
        if not cg_ok:
            print(f"| {N} | FAIL | - | - | - | - | - | - |")
            print(f"--> Codegen error for N={N}:\n{cg_err}")
            break
            
        go_file = edda_file.replace(".edda", ".go")
        file_size = os.path.getsize(go_file)
        
        # Format for tests
        postprocess_emulator_go(N, go_file)
        generate_native(N, "native.go", nodes)
        generate_benchmark_test(N, "bench_test.go")
        
        subprocess.run(["go", "mod", "tidy"], capture_output=True)
        
        bench_ok, bench_out = run_benchmarks()
        
        if not bench_ok:
            print(f"| {N} | OK | FAIL | - | {file_size} | - | - | - |")
            print(f"--> Bench error for N={N}:\n{bench_out}")
            break
            
        emu_ns, nat_ns = parse_benchmark_ns(bench_out)
        overhead = emu_ns / nat_ns if nat_ns > 0 else 0
        
        print(f"| {N} | OK | OK | {cg_time:.4f}s | {file_size} | {emu_ns:.2f} | {nat_ns:.2f} | {overhead:.2f}x |")

if __name__ == "__main__":
    main()
