import requests
import base64

# Test with a small image first
with open('C:/Users/0501JP/mmx/renders/frame_0001.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "tempura-qwen2.5-vl-3b",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What do you see in this image? One paragraph."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        ]
    }],
    "max_tokens": 200,
    "temperature": 0.3
}

resp = requests.post("http://localhost:1234/v1/chat/completions", json=payload, timeout=120)
print(resp.status_code)
if resp.status_code == 200:
    print(resp.json()['choices'][0]['message']['content'])
else:
    print(resp.text)
