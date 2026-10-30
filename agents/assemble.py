import bpy, os
from pathlib import Path

# Define STL files in assembly order (logical construction sequence)
stl_files = [
    "1_PAF(stand).stl",  # Base structure
    "2_PropM(Lower).stl",  # Lower propulsion
    "3_PropM(Upper).stl",  # Upper propulsion
    "4_ReturnM(Lower).stl",  # Lower return module
    "5_RetunM(Upper).stl",  # Upper return module
    "6_ExplorationM.stl",  # Exploration module
    "7_LandingLeg(normal).stl",  # Landing leg (normal)
    "8_LandingLeg(P-SMP).stl",  # Landing leg (P-SMP)
    "9_SolarPaddle.stl",  # Solar paddle
    "10_Miscellaneous.stl"  # Misc components
]

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import each STL
for filename in stl_files:
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    if os.path.exists(filepath):
        # Import STL
        bpy.ops.import_mesh.stl(filepath=filepath)
        # Get the last imported object
        obj = bpy.context.active_object
        if obj:
            # Rename object to match filename
            obj.name = filename.replace(".stl", "")
            # Optional: set origin to geometry
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            print(f"Imported: {obj.name} ({len(obj.data.polygons)} faces)")
    else:
        print(f"Warning: {filepath} not found")

# Set up scene
bpy.context.scene.view_3d.view_perspective = 'TOP'
bpy.context.scene.camera.location = (0, -10, 5)
bpy.context.scene.camera.rotation_euler = (1.0, 0, 0)

# Set render engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'

print("Assembly complete!")
