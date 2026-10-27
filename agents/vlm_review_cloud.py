"""
VLM Review Agent - Cloud API fallback (Gemini / OpenAI GPT-4V)
Used when LM Studio not available (e.g., GitHub Actions cloud runners)
"""
import sys
import os
import base64
import json
import requests
from pathlib import Path

ROOT = Path(__file__).parent.parent
RENDERS_DIR = ROOT / "renders"

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_gemini(image_path, prompt=None):
    """Analyze using Google Gemini Vision API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: GEMINI_API_KEY not set"
    
    if prompt is None:
        prompt = """Analyze this MMX spacecraft animation frame. Describe:
1. Spacecraft visibility and orientation
2. Lighting quality (space environment, sun direction)
3. Color scheme accuracy (JAXA MMX: white thermal blankets, red propulsion, blue solar panels, gray structure)
4. Camera composition (orbital motion, framing)
5. Any visual artifacts or issues
6. Overall cinematic quality (1-10)"""
    
    b64 = encode_image(image_path)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": b64}}
            ]
        }],
        "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.3}
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Gemini API Error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Gemini connection error: {e}"

def analyze_openai(image_path, prompt=None):
    """Analyze using OpenAI GPT-4V API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY not set"
    
    if prompt is None:
        prompt = """Analyze this MMX spacecraft animation frame. Describe:
1. Spacecraft visibility and orientation
2. Lighting quality (space environment, sun direction)
3. Color scheme accuracy (JAXA MMX: white thermal blankets, red propulsion, blue solar panels, gray structure)
4. Camera composition (orbital motion, framing)
5. Any visual artifacts or issues
6. Overall cinematic quality (1-10)"""
    
    b64 = encode_image(image_path)
    
    payload = {
        "model": "gpt-4o",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }],
        "max_tokens": 1000,
        "temperature": 0.3
    }
    
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"OpenAI API Error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"OpenAI connection error: {e}"

def review_keyframes():
    """Review key frames using available cloud API."""
    frames = sorted(RENDERS_DIR.glob("frame_*.png"))
    if not frames:
        print("No frames found in renders/")
        return
    
    key_indices = [0, len(frames)//3, 2*len(frames)//3, -1]
    key_frames = [frames[i] for i in key_indices]
    
    print(f"Reviewing {len(key_frames)} key frames from {len(frames)} total...")
    
    # Prefer Gemini (cheaper/faster), fallback to OpenAI
    analyzer = None
    if os.getenv("GEMINI_API_KEY"):
        analyzer = ("Gemini", analyze_gemini)
    elif os.getenv("OPENAI_API_KEY"):
        analyzer = ("OpenAI", analyze_openai)
    else:
        print("ERROR: No cloud API keys configured (GEMINI_API_KEY or OPENAI_API_KEY)")
        return
    
    print(f"Using {analyzer[0]} API")
    reviews = {}
    
    for i, frame in enumerate(key_frames):
        frame_num = int(frame.stem.split('_')[1])
        print(f"\n{'='*60}")
        print(f"Frame {frame_num} ({frame.name})")
        print(f"{'='*60}")
        
        review = analyzer[1](frame)
        reviews[f"frame_{frame_num}"] = review
        print(review)
    
    # Save reviews
    out_file = ROOT / "vlm_reviews.json"
    with open(out_file, 'w') as f:
        json.dump(reviews, f, indent=2)
    print(f"\nSaved reviews to {out_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("VLM Cloud Review Agent")
        print("Usage: python agents/vlm_review_cloud.py keyframes")
        print("Requires: GEMINI_API_KEY or OPENAI_API_KEY environment variable")
        sys.exit(0)
    
    if sys.argv[1] == "keyframes":
        review_keyframes()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)