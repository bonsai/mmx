import requests
import base64

frames = [1, 150, 300, 450]
for frame_num in frames:
    path = f'C:/Users/0501JP/mmx/renders/frame_{frame_num:04d}.png'
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": "tempura-qwen2.5-vl-3b",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "This is a frame from a JAXA MMX spacecraft animation. Describe: 1) Spacecraft visibility and parts visible, 2) Lighting and space environment, 3) Colors visible, 4) Camera angle, 5) Any issues. Be specific."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }],
        "max_tokens": 300,
        "temperature": 0.3
    }
    
    resp = requests.post("http://localhost:1234/v1/chat/completions", json=payload, timeout=120)
    if resp.status_code == 200:
        content = resp.json()['choices'][0]['message']['content']
        print(f"\n=== Frame {frame_num} ===")
        print(content)
    else:
        print(f"Frame {frame_num} ERROR: {resp.text}")
