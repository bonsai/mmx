"""
Blender Agent - Automates MMX spacecraft modeling tasks in Blender via bpy.
Run: blender --background --python agents/blender_agent.py -- [command] [args]
"""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

COMMANDS = {
    "import_stl": "Import STL files and assemble MMX",
    "apply_colors": "Apply materials from mmx_colors.json",
    "decimate": "Create low-poly version (5% ratio)",
    "animate": "Create 15s space flight animation",
    "render": "Render animation frames",
    "export_glb": "Export to GLB for web viewer",
    "full_pipeline": "Run complete pipeline: import -> color -> decimate -> animate -> render -> export",
}

def import_stl():
    """Import all 10 STL components."""
    from build_full_colored2 import main as import_main
    import_main()

def apply_colors():
    """Apply materials from JSON config."""
    from apply_colors2 import main as color_main
    color_main()

def decimate():
    """Create low-poly version."""
    from decimate_colored2 import main as decimate_main
    decimate_main()

def animate():
    """Create animation scene."""
    from create_animation_fast import main as anim_main
    anim_main()

def render():
    """Render animation frames."""
    import bpy
    bpy.ops.render.render(animation=True)

def export_glb():
    """Export colored low-poly to GLB."""
    import bpy
    bpy.ops.wm.open_mainfile(filepath="models/mmx_colored_lowpoly.blend")
    bpy.ops.export_scene.gltf(
        filepath="web/models/mmx.glb",
        export_format='GLB',
        use_selection=False,
    )

def full_pipeline():
    """Run complete pipeline."""
    import_stl()
    apply_colors()
    decimate()
    animate()
    render()
    export_glb()

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("MMX Blender Agent")
        print("Usage: blender --background --python agents/blender_agent.py -- <command>")
        print("\nCommands:")
        for cmd, desc in COMMANDS.items():
            print(f"  {cmd:20s} - {desc}")
        sys.exit(0)
    
    # Handle Blender's argument passing (after --)
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    command = args[0]
    
    if command == "import_stl":
        import_stl()
    elif command == "apply_colors":
        apply_colors()
    elif command == "decimate":
        decimate()
    elif command == "animate":
        animate()
    elif command == "render":
        render()
    elif command == "export_glb":
        export_glb()
    elif command == "full_pipeline":
        full_pipeline()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)