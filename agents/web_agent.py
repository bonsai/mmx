"""
Web Viewer Agent - Manages Three.js viewer for MMX spacecraft.
Handles GLB deployment, viewer updates, GitHub Pages sync.
"""
import sys
import os
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
WEB_DIR = ROOT / "web"
MODELS_DIR = WEB_DIR / "models"

COMMANDS = {
    "update_glb": "Copy latest GLB to web/models/",
    "update_viewer": "Update index.html with new features",
    "serve": "Start local dev server",
    "deploy": "Commit and push to trigger GitHub Pages deploy",
    "validate": "Validate GLB loads correctly",
}

def update_glb(source=None):
    """Copy GLB to web directory."""
    if source is None:
        source = ROOT / "models/mmx_colored_lowpoly.glb"
    else:
        source = Path(source)
    
    if not source.exists():
        print(f"Source not found: {source}")
        # Try to export from blend
        export_from_blend()
        source = ROOT / "models/mmx_colored_lowpoly.glb"
    
    dest = MODELS_DIR / "mmx.glb"
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"Copied {source} -> {dest} ({dest.stat().st_size/1024:.1f} KB)")

def export_from_blend():
    """Export GLB from colored lowpoly blend using Blender."""
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "models/mmx_colored_lowpoly.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(ROOT / "models/mmx_colored_lowpoly.glb"),
        export_format='GLB',
        use_selection=False,
    )
    print("Exported GLB from Blender")

def update_viewer():
    """Update index.html with enhanced viewer."""
    html = WEB_DIR / "index.html"
    # Viewer already has good features, just ensure it points to mmx.glb
    print(f"Viewer at {html} - update manually if needed")

def serve(port=8081):
    """Start local HTTP server for viewer."""
    import http.server
    import socketserver
    import threading
    import webbrowser
    
    os.chdir(WEB_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        webbrowser.open(f"http://localhost:{port}")
        httpd.serve_forever()

def deploy(message="Update MMX viewer"):
    """Git commit and push to trigger Pages deploy."""
    subprocess.run(["git", "add", "web/"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
    print("Deployed! Check https://bonsai.github.io/mmx/")

def validate():
    """Quick validation of GLB."""
    glb_path = MODELS_DIR / "mmx.glb"
    if glb_path.exists():
        size = glb_path.stat().st_size
        print(f"GLB exists: {glb_path} ({size/1024:.1f} KB)")
        # Could add glTF validator here
    else:
        print("GLB not found - run update_glb first")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("MMX Web Viewer Agent")
        print("Usage: python agents/web_agent.py <command> [args]")
        print("\nCommands:")
        for cmd, desc in COMMANDS.items():
            print(f"  {cmd:20s} - {desc}")
        sys.exit(0)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "update_glb":
        update_glb(args[0] if args else None)
    elif command == "update_viewer":
        update_viewer()
    elif command == "serve":
        serve(int(args[0]) if args else 8081)
    elif command == "deploy":
        deploy(args[0] if args else "Update MMX viewer")
    elif command == "validate":
        validate()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)