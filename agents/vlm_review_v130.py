import requests
import base64
import json
from pathlib import Path

RENDERS_DIR = Path("C:/Users/0501JP/mmx/tmp/renders_v130")
LMSTUDIO_API = "http://localhost:1234/v1/chat/completions"

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_frame(image_path, frame_num):
    b64 = encode_image(image_path)
    
    prompt = """Analyze this MMX spacecraft animation frame (v1.3.0 - camera pull-back version).
Describe:
1. Spacecraft visibility - can you see the full spacecraft clearly?
2. Camera framing - is the spacecraft well-framed, not too close/cluttered?
3. Lighting - are colors visible? (white thermal blankets, red/orange propulsion, dark blue solar panels, gray structure)
4. Composition - clean orbital view or cluttered?
5. Any geometry issues (collapsing, artifacts)?
6. Overall cinematic quality (1-10)

Compare to v1.2.0 issues: camera was too close/cluttered, geometry concerns."""
    
    payload = {
        "model": "tempura-qwen2.5-vl-3b",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }],
        "max_tokens": 800,
        "temperature": 0.3
    }
    
    try:
        resp = requests.post(LMSTUDIO_API, json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {e}"

# Sample key frames: start, 33%, 66%, end
frames = sorted(RENDERS_DIR.glob("frame_*.png"))
if not frames:
    print("No frames found")
    exit(1)

key_indices = [0, len(frames)//3, 2*len(frames)//3, -1]
key_frames = [frames[i] for i in key_indices]

print(f"Reviewing v1.3.0 - {len(key_frames)} key frames from {len(frames)} total")
print("="*70)

reviews = {}
for frame in key_frames:
    frame_num = int(frame.stem.split('_')[1])
    print(f"\n--- Frame {frame_num} ({frame.name}) ---")
    review = analyze_frame(frame, frame_num)
    reviews[f"frame_{frame_num}"] = review
    print(review)

# Save
out_file = Path("C:/Users/0501JP/mmx/db/vlm_review_v130.json")
with open(out_file, 'w') as f:
    json.dump(reviews, f, indent=2)
print(f"\nSaved to {out_file}")

# Summary
print("\n" + "="*70)
print("v1.3.0 VLM REVIEW SUMMARY")
print("="*70)
for k, v in reviews.items():
    print(f"\n--- {k} ---")
    print(v[:600] + "..." if len(v) > 600 else v)
