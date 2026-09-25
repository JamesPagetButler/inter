import json
import time
import os
from google import genai

# Load hypergraph data
with open('hypergraph_dataset.json', 'r') as f:
    data = json.load(f)

# We want Gemini to find the target node starting from node_0000 using the golden paths.
# To not blow up context window, we'll give it the list of golden paths and ask it to trace the path from node_0000.
# The sequence is length 100.
prompt = f"""
You are a topological graph traverser.
I will give you a list of valid triad transitions (Golden Paths) in a hypergraph.
Start at 'node_0000' and trace the path step-by-step using ONLY the provided golden paths.
The paths are defined as triads: NodeA|NodeB|NodeC.
When you are at NodeA and NodeB, the next step is NodeC.
The first two nodes in the sequence are 'node_0000' and 'node_0002'.

Here are the valid transitions:
{list(data['golden_paths'].keys())}

Follow the path to the end and tell me the final node ID.
"""

client = genai.Client()

print("Starting Gemini Inference...")
start_time = time.time()

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    end_time = time.time()
    
    print(f"Gemini Inference Time: {end_time - start_time:.3f} seconds")
    print(f"Response:\n{response.text[:500]}...\n(Truncated for brevity)")
except Exception as e:
    print(f"Error calling Gemini: {e}")
