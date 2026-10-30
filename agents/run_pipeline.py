#!/usr/bin/env python3
"""
Master Pipeline Orchestrator - Runs complete MMX workflow.
Usage: python agents/run_pipeline.py [--skip-blender] [--skip-web]
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent

def run_blender_script(script_name, description):
    """Run a Blender Python script."""
    script_path = ROOT / script_name
    if not script_path.exists():
        script_path = ROOT / "agents" / script_name
    if not script_path.exists():
        print(f"Script not found: {script_name}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")
    
    result = subprocess.run([
        "blender", "--background", "--python", str(script_path)
    ], capture_output=True, text=True, timeout=300)
    
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    return True

def main():
    parser = argparse.ArgumentParser(description="MMX Full Pipeline")
    parser.add_argument("--skip-blender", action="store_true", help="Skip Blender steps")
    parser.add_argument("--skip-web", action="store_true", help="Skip web deployment")
    parser.add_argument("--only", choices=["import", "color", "decimate", "animate", "render", "export", "deploy"], help="Run only one step")
    args = parser.parse_args()
    
    steps = [
        ("build_full_colored2.py", "Import STLs + Apply Colors"),
        # Decimation is included in build_full_colored2.py
        ("create_animation_fast.py", "Create Animation Scene"),
        # Render would be: ("render_animation.py", "Render Frames"),
        # Export GLB would be separate
    ]
    
    if args.only:
        step_map = {
            "import": "build_full_colored2.py",
            "animate": "create_animation_fast.py",
        }
        if args.only in step_map:
            run_blender_script(step_map[args.only], args.only)
        return
    
    if not args.skip_blender:
        for script, desc in steps:
            if not run_blender_script(script, desc):
                print(f"Pipeline failed at: {desc}")
                return 1
    
    # Export GLB
    if not args.skip_web:
        print("\nExporting GLB...")
        subprocess.run([sys.executable, "-m", "agents.web_agent", "update_glb"], cwd=ROOT)
        subprocess.run([sys.executable, "-m", "agents.web_agent", "validate"], cwd=ROOT)
        
        if not args.skip_web:
            print("\nDeploying to GitHub Pages...")
            subprocess.run([sys.executable, "-m", "agents.web_agent", "deploy", "Pipeline deploy"], cwd=ROOT)
    
    print("\n✅ Pipeline complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
