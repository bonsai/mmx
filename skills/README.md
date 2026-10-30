# VLM Reviewer Skill for Pi Coding Agent

## Overview
The `vlm_reviewer` skill provides programmatic access to Vision-Language Models for reviewing rendered frames. Supports multiple providers (LM Studio, OpenAI, Gemini, Ollama) with MMX-specific preset prompts.

## Installation
```bash
# No additional install needed - uses stdlib + requests
# Ensure requests is available: pip install requests
```

## Quick Start
```python
from skills.vlm_reviewer import VLMReviewerSkill, VLMConfig, VLMProvider, MMX_REVIEW_PROMPTS

# Create reviewer (defaults to LM Studio local)
reviewer = VLMReviewerSkill()

# Or configure for cloud
reviewer = VLMReviewerSkill(VLMConfig(
    provider=VLMProvider.GEMINI,
    model="gemini-1.5-flash",
    api_key="your-key"
))

# Review frames
frames = reviewer.load_frames_from_dir("tmp/renders_v130", sample_rate=75)  # 4 frames
results = reviewer.review_frames(frames, MMX_REVIEW_PROMPTS["full"])

for r in results:
    print(f"Frame {r.frame_num}: {r.response[:200]}...")
```

## CLI Usage
```bash
# Review 4 frames from directory with full MMX prompt
python skills/vlm_reviewer.py tmp/renders_v130 --sample 4

# Quick assessment only
python skills/vlm_reviewer.py tmp/renders_v130 --prompt quick --sample 8

# Lighting-focused review
python skills/vlm_reviewer.py tmp/renders_v130 --prompt lighting

# Use cloud Gemini
python skills/vlm_reviewer.py tmp/renders_v130 --provider gemini --model gemini-1.5-flash

# Save results
python skills/vlm_reviewer.py tmp/renders_v130 --output db/vlm_review_latest.json
```

## Configuration

### VLMConfig Options
```python
VLMConfig(
    provider=VLMProvider.LMSTUDIO,  # LMSTUDIO, OPENAI, GEMINI, OLLAMA, CUSTOM
    model="tempura-qwen2.5-vl-3b",  # Model name
    api_base="http://localhost:1234/v1",  # API endpoint
    api_key=None,  # For OpenAI/Gemini
    max_tokens=1000,
    temperature=0.3,
    timeout=120
)
```

### Providers
| Provider | API Base | Auth | Notes |
|----------|----------|------|-------|
| LM Studio | `http://localhost:1234/v1` | None | Local, free |
| OpenAI | `https://api.openai.com/v1` | `OPENAI_API_KEY` | GPT-4V |
| Gemini | `https://generativelanguage.googleapis.com` | `GEMINI_API_KEY` | Fast, cheap |
| Ollama | `http://localhost:11434` | None | Local |
| Custom | Any OpenAI-compatible | Optional | Flexible |

## MMX Preset Prompts
```python
from skills.vlm_reviewer import MMX_REVIEW_PROMPTS

MMX_REVIEW_PROMPTS["full"]      # Complete 7-category review
MMX_REVIEW_PROMPTS["lighting"]  # Lighting only
MMX_REVIEW_PROMPTS["colors"]    # Color accuracy only
MMX_REVIEW_PROMPTS["camera"]    # Camera framing only
MMX_REVIEW_PROMPTS["geometry"]  # Mesh integrity only
MMX_REVIEW_PROMPTS["quick"]     # 2-3 sentence summary
```

## Advanced Usage

### Batch Review Different Aspects
```python
results = reviewer.batch_review(frames, {
    "lighting": MMX_REVIEW_PROMPTS["lighting"],
    "colors": MMX_REVIEW_PROMPTS["colors"],
    "camera": MMX_REVIEW_PROMPTS["camera"],
})
```

### Compare Versions
```python
comparison = reviewer.compare_versions(
    v1_frames=["tmp/renders_v120/frame_0001.png"],
    v2_frames=["tmp/renders_v130/frame_0001.png"],
    criteria=["visibility", "colors", "camera", "composition"]
)
```

### Save/Load Results
```python
reviewer.save_results(results, Path("db/vlm_review_v130.json"))
```

## Integration with Pipeline
```python
from skills.pipeline import stage_review_vlm

# In pipeline.py
def stage_review_vlm(args):
    reviewer = create_reviewer("lmstudio", "tempura-qwen2.5-vl-3b")
    frames = reviewer.load_frames_from_dir(f"tmp/renders_{args.tag}", sample_rate=75)
    results = reviewer.review_frames(frames, MMX_REVIEW_PROMPTS["full"])
    reviewer.save_results(results, Path(f"db/vlm_review_{args.tag}.json"))
```

## Troubleshooting

### LM Studio Timeout on High-Res Frames
```python
# Resize frames first
from PIL import Image
for f in Path("tmp/renders_v130").glob("frame_*.png"):
    img = Image.open(f)
    img.thumbnail((1280, 720))
    img.save(f)

# Or use cloud provider
reviewer = create_reviewer("gemini", "gemini-1.5-flash")
```

### No LM Studio Running
```bash
# Start LM Studio server
lms server start --port 1234
# Load model
lms load tempura-qwen2.5-vl-3b
```

## File Structure
```
skills/
├── __init__.py
├── vlm_reviewer.py      # Main skill
├── pipeline.py          # Pipeline integration
└── base.py              # Base Skill class (if exists)
```