"""
VLM Review Agent - Uses LM Studio (Qwen2.5-VL) to review rendered frames.
"""
import sys
import os
import base64
import json
import requests
from pathlib import Path

ROOT = Path(__file__).parent.parent
RENDERS_DIR = ROOT / "renders"
LMSTUDIO_API = "http://localhost:1234/v1/chat/completions"

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_frame(image_path, prompt=None):
    """Send frame to LM Studio VLM for analysis."""
    if prompt is None:
        prompt = """Analyze this MMX spacecraft animation frame. Describe:
1. Spacecraft visibility and orientation
2. Lighting quality (space environment, sun direction)
3. Color scheme accuracy (JAXA MMX: white thermal blankets, red propulsion, blue solar panels, gray structure)
4. Camera composition (orbital motion, framing)
5. Any visual artifacts or issues
6. Overall cinematic quality (1-10)

Be specific and critical - this is for improving the animation."""
    
    b64 = encode_image(image_path)
    
    payload = {
        "model": "tempura-qwen2.5-vl-3b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.3
    }
    
    try:
        resp = requests.post(LMSTUDIO_API, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"

def review_keyframes():
    """Review key frames: start, middle, end."""
    frames = sorted(RENDERS_DIR.glob("frame_*.png"))
    if not frames:
        print("No frames found in renders/")
        return
    
    key_indices = [0, len(frames)//3, 2*len(frames)//3, -1]
    key_frames = [frames[i] for i in key_indices]
    
    print(f"Reviewing {len(key_frames)} key frames from {len(frames)} total...")
    
    reviews = {}
    for i, frame in enumerate(key_frames):
        frame_num = int(frame.stem.split('_')[1])
        print(f"\n{'='*60}")
        print(f"Frame {frame_num} ({frame.name})")
        print(f"{'='*60}")
        
        review = analyze_frame(frame)
        reviews[f"frame_{frame_num}"] = review
        print(review)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for k, v in reviews.items():
        print(f"\n--- {k} ---")
        print(v[:500] + "..." if len(v) > 500 else v)
    
    # Save reviews
    out_file = ROOT / "vlm_reviews.json"
    with open(out_file, 'w') as f:
        json.dump(reviews, f, indent=2)
    print(f"\nSaved reviews to {out_file}")

def review_video_frames(sample_rate=30):
    """Review frames at intervals (e.g., every 30 frames = 1 second)."""
    frames = sorted(RENDERS_DIR.glob("frame_*.png"))
    if not frames:
        print("No frames found")
        return
    
    sampled = frames[::sample_rate]
    print(f"Reviewing {len(sampled)} frames (every {sample_rate} frames)...")
    
    for frame in sampled:
        frame_num = int(frame.stem.split('_')[1])
        print(f"\n--- Frame {frame_num} ---")
        review = analyze_frame(frame)
        print(review[:300] + "..." if len(review) > 300 else review)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("VLM Review Agent")
        print("Usage: python agents/vlm_review.py <command>")
        print("  keyframes  - Review 4 key frames (start, 33%, 66%, end)")
        print("  video      - Review every N frames (default 30)")
        print("  frame N    - Review specific frame number")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "keyframes":
        review_keyframes()
    elif command == "video":
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        review_video_frames(sample)
    elif command == "frame":
        if len(sys.argv) < 3:
            print("Usage: frame <number>")
            sys.exit(1)
        frame_path = RENDERS_DIR / f"frame_{int(sys.argv[2]):04d}.png"
        if frame_path.exists():
            print(analyze_frame(frame_path))
        else:
            print(f"Frame not found: {frame_path}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
