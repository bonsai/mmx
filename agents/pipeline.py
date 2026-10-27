#!/usr/bin/env python3
"""
MMX Pipeline Controller - Gen/Render -> Review/VLM -> Review/User -> Re-Gen
Usage: python agents/pipeline.py <stage> [options]
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "db/mmx_history.db"

STAGES = {
    "gen": "Generate Blender scene from presets/ontology",
    "render": "Render animation frames to video",
    "review-vlm": "Run VLM review on rendered frames",
    "review-user": "Interactive user feedback collection",
    "regen": "Regenerate with applied feedback",
    "export-glb": "Export GLB for web viewer",
    "deploy": "Deploy to GitHub Pages",
    "full": "Run complete cycle: gen -> render -> review-vlm -> (review-user) -> regen",
}

def run_blender(script, desc):
    print(f"\n>>> {desc}")
    result = subprocess.run([
        "blender", "--background", "--python", str(ROOT / script)
    ], capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    return True

def run_ffmpeg(frames_dir, output_video, fps=30):
    print(f"\n>>> Creating video: {output_video}")
    result = subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", str(output_video)
    ], capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    print("Video created:", output_video)
    return True

def stage_gen(args):
    preset = args.preset or "orbital_standard"
    print(f"Generating scene with preset: {preset}")
    return run_blender("agents/blender_agent.py", f"Generate scene ({preset})")

def stage_render(args):
    blend_file = args.blend or "models/mmx_animation_v130.blend"
    frames_dir = ROOT / f"tmp/renders_{args.tag or 'v130'}"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Rendering {blend_file} -> {frames_dir}")
    result = subprocess.run([
        "blender", "-b", str(ROOT / blend_file), "-o", str(frames_dir / "frame_"), "-a"
    ], capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    
    video_file = ROOT / f"video/MMX_space_flight_{args.tag or 'v130'}.mp4"
    return run_ffmpeg(frames_dir, video_file)

def stage_review_vlm(args):
    frames_dir = ROOT / f"tmp/renders_{args.tag or 'v130'}"
    if not frames_dir.exists():
        print(f"Frames not found: {frames_dir}")
        return False
    
    import requests, base64, json
    frames = sorted(frames_dir.glob("frame_*.png"))
    key_indices = [0, len(frames)//3, 2*len(frames)//3, -1]
    key_frames = [frames[i] for i in key_indices]
    
    LMSTUDIO_API = "http://localhost:1234/v1/chat/completions"
    
    reviews = {}
    for frame in key_frames:
        frame_num = int(frame.stem.split('_')[1])
        with open(frame, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        
        payload = {
            "model": "tempura-qwen2.5-vl-3b",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Review this MMX spacecraft frame: visibility, colors, camera framing, geometry issues, overall quality (1-10)."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]
            }],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        try:
            resp = requests.post(LMSTUDIO_API, json=payload, timeout=120)
            if resp.status_code == 200:
                reviews[f"frame_{frame_num}"] = resp.json()['choices'][0]['message']['content']
                print(f"Frame {frame_num}: OK")
            else:
                reviews[f"frame_{frame_num}"] = f"API Error: {resp.status_code}"
        except Exception as e:
            reviews[f"frame_{frame_num}"] = f"Error: {e}"
    
    out_file = ROOT / f"db/vlm_review_{args.tag or 'v130'}.json"
    with open(out_file, 'w') as f:
        json.dump(reviews, f, indent=2)
    print(f"VLM review saved to {out_file}")
    return True

def stage_review_user(args):
    print("\n=== USER FEEDBACK COLLECTION ===")
    print("Video location:", ROOT / f"video/MMX_space_flight_{args.tag or 'v130'}.mp4")
    print("Open video and provide feedback:")
    
    feedback_items = []
    while True:
        print("\n--- New Feedback ---")
        source = "user"
        category = input("Category (lighting/color/camera/composition/geometry/performance/other): ").strip().lower()
        if not category:
            break
        severity = int(input("Severity (1=Low, 2=Major, 3=Critical): ") or "2")
        title = input("Title: ").strip()
        description = input("Description: ").strip()
        suggestion = input("Suggestion: ").strip()
        
        feedback_items.append({
            "source": source,
            "category": category,
            "severity": severity,
            "title": title,
            "description": description,
            "suggestion": suggestion
        })
        
        if input("Add more? (y/N): ").lower() != 'y':
            break
    
    if feedback_items:
        import sqlite3
        from datetime import datetime
        db = sqlite3.connect(DB)
        cur = db.cursor()
        cur.execute("SELECT id FROM versions ORDER BY id DESC LIMIT 1")
        latest_version_id = cur.fetchone()[0]
        
        for fb in feedback_items:
            cur.execute("""
                INSERT INTO feedback (version_id, source, category, severity, title, description, suggestion, addressed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (latest_version_id, fb['source'], fb['category'], fb['severity'], fb['title'], fb['description'], fb['suggestion'], datetime.now().isoformat()))
        db.commit()
        print(f"Saved {len(feedback_items)} feedback items to database.")
    return True

def stage_regen(args):
    print("Regenerating with applied feedback...")
    return stage_gen(args)

def stage_export_glb(args):
    blend_file = args.blend or "models/mmx_colored_lowpoly.blend"
    output = ROOT / "web/models/mmx.glb"
    print(f"Exporting {blend_file} -> {output}")
    result = subprocess.run([
        "blender", "--background", "--python", "-c", f"""
import bpy
bpy.ops.wm.open_mainfile(filepath=r\"{ROOT / blend_file}\")
bpy.ops.export_scene.gltf(filepath=r\"{output}\", export_format='GLB', use_selection=False)
print(\"Exported GLB\")
"""
    ], capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    print("GLB exported to", output)
    return True

def stage_deploy(args):
    print("Deploying to GitHub Pages...")
    subprocess.run(["git", "add", "web/"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", f"Deploy v{args.tag or '130'} viewer"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
    print("Deployed! Check https://bonsai.github.io/mmx/")
    return True

def main():
    parser = argparse.ArgumentParser(description="MMX Pipeline Controller")
    parser.add_argument("stage", choices=list(STAGES.keys()) + ["help"], help="Pipeline stage")
    parser.add_argument("--preset", help="Camera preset for gen stage")
    parser.add_argument("--blend", help="Blend file for render stage")
    parser.add_argument("--tag", help="Version tag (e.g., v130)")
    parser.add_argument("--list-presets", action="store_true", help="List available presets")
    args = parser.parse_args()
    
    if args.stage == "help" or len(sys.argv) == 1:
        print("MMX Pipeline Controller")
        print("Usage: python agents/pipeline.py <stage> [options]")
        print("\nStages:")
        for s, d in STAGES.items():
            print(f"  {s:<15} - {d}")
        print("\nOptions:")
        print("  --preset <name>     Camera preset for gen")
        print("  --blend <file>      Blend file for render")
        print("  --tag <tag>         Version tag (e.g., v130)")
        print("  --list-presets      List available presets")
        return
    
    if args.list_presets:
        import yaml
        with open(ROOT / "cinematic_presets.yml") as f:
            presets = yaml.safe_load(f)
        for k, v in presets.items():
            if isinstance(v, dict) and 'name' in v:
                print(f"  {k:<20} - {v['name']}")
        return
    
    handlers = {
        "gen": stage_gen,
        "render": stage_render,
        "review-vlm": stage_review_vlm,
        "review-user": stage_review_user,
        "regen": stage_regen,
        "export-glb": stage_export_glb,
        "deploy": stage_deploy,
    }
    
    if args.stage in handlers:
        success = handlers[args.stage](args)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown stage: {args.stage}")
        sys.exit(1)

if __name__ == "__main__":
    main()