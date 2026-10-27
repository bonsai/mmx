import bpy, os, math
from mathutils import Vector, Euler

# Load low-poly scene
blend_file = "C:/Users/0501JP/mmx/models/mmx_lowpoly.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Get the MMX object
mmx_obj = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'MMX' in obj.name:
        mmx_obj = obj
        break

if not mmx_obj:
    mmx_obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print(f"Animating: {mmx_obj.name}")

# Scene settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 450  # 15 seconds @ 30 fps

# Clear existing animation
bpy.ops.object.select_all(action='SELECT')
for obj in bpy.context.selected_objects:
    obj.animation_data_clear()
bpy.ops.object.select_all(action='DESELECT')

# ===== CAMERA SETUP =====
cam_data = bpy.data.cameras.new('AnimCamera')
cam_obj = bpy.data.objects.new('AnimCamera', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Camera lens for space feel
cam_data.lens = 35
cam_data.clip_start = 0.1
cam_data.clip_end = 1000

# ===== WORLD: Space environment =====
world = bpy.data.worlds.new("SpaceWorld")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear default nodes
for n in nodes:
    nodes.remove(n)

# Background node - space gradient
bg = nodes.new('ShaderNodeBackground')
bg.location = (0, 0)
bg.inputs[0].default_value = (0.01, 0.01, 0.02, 1.0)  # Deep space black
bg.inputs[1].default_value = 0.1

# Add star texture
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-600, 0)

noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 0)
noise.inputs['Scale'].default_value = 200
noise.inputs['Detail'].default_value = 8
noise.inputs['Roughness'].default_value = 0.7
noise.inputs['Distortion'].default_value = 0.0

color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (-200, 0)
color_ramp.color_ramp.elements[0].position = 0.95
color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
color_ramp.color_ramp.elements[1].position = 0.98
color_ramp.color_ramp.elements[1].color = (1, 1, 0.9, 1)

mix = nodes.new('ShaderNodeMixRGB')
mix.location = (0, -200)
mix.blend_type = 'MIX'
mix.inputs['Fac'].default_value = 1.0
mix.inputs[1].default_value = (0.01, 0.01, 0.02, 1.0)
mix.inputs[2].default_value = (1, 1, 0.9, 1)

output = nodes.new('ShaderNodeOutputWorld')
output.location = (200, 0)

links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], mix.inputs['Color2'])
links.new(mix.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])

# ===== LIGHTING =====
# Sun (distant star)
sun_data = bpy.data.lights.new('Sun', 'SUN')
sun_obj = bpy.data.objects.new('Sun', sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = Euler((math.radians(45), math.radians(30), 0), 'XYZ')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.95, 0.9)
sun_data.angle = 0.53

# Fill light
fill_data = bpy.data.lights.new('Fill', 'SUN')
fill_obj = bpy.data.objects.new('Fill', fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = Euler((math.radians(-45), math.radians(-30), 0), 'XYZ')
fill_data.energy = 0.5
fill_data.color = (0.3, 0.4, 0.6)

# Rim light
rim_data = bpy.data.lights.new('Rim', 'SUN')
rim_obj = bpy.data.objects.new('Rim', rim_data)
scene.collection.objects.link(rim_obj)
rim_obj.rotation_euler = Euler((math.radians(180), 0, 0), 'XYZ')
rim_data.energy = 0.3
rim_data.color = (0.2, 0.3, 0.5)

# ===== MMX OBJECT ANIMATION: Flying through space =====
# Initial position
mmx_obj.location = (0, 0, 0)
mmx_obj.rotation_euler = Euler((0, 0, 0), 'XYZ')
mmx_obj.scale = (1, 1, 1)

# Keyframe 1: Start
mmx_obj.keyframe_insert(data_path="location", frame=1)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=1)

# Keyframe 150 (5s): Move forward + slight turn
mmx_obj.location = (10, -30, 5)
mmx_obj.rotation_euler = Euler((math.radians(10), math.radians(15), math.radians(5)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=150)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=150)

# Keyframe 300 (10s): Continue flight + banking
mmx_obj.location = (25, -70, 12)
mmx_obj.rotation_euler = Euler((math.radians(-5), math.radians(30), math.radians(-10)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=300)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=300)

# Keyframe 450 (15s): Final position
mmx_obj.location = (40, -120, 20)
mmx_obj.rotation_euler = Euler((math.radians(15), math.radians(45), math.radians(8)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=450)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=450)

# Set interpolation to Bezier for smooth motion
for fcurve in mmx_obj.animation_data.action.fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'BEZIER'

# ===== CAMERA ANIMATION: Orbiting around MMX while following =====
# Camera follows MMX with orbital motion
cam_distance = 25
cam_height = 10

for frame in range(1, 451, 5):  # Keyframe every 5 frames
    scene.frame_set(frame)
    
    # Get MMX position at this frame
    mmx_loc = mmx_obj.matrix_world.translation
    
    # Orbital angle around MMX (360° over 15 seconds = 24°/sec)
    orbit_angle = (frame - 1) * (2 * math.pi / 450) * 2  # 2 full orbits
    
    # Camera position relative to MMX
    cam_x = mmx_loc.x + cam_distance * math.sin(orbit_angle)
    cam_y = mmx_loc.y + cam_distance * math.cos(orbit_angle) - 15  # Behind
    cam_z = mmx_loc.z + cam_height + 5 * math.sin(orbit_angle * 2)  # Vertical oscillation
    
    cam_obj.location = (cam_x, cam_y, cam_z)
    
    # Camera looks at MMX
    direction = mmx_loc - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    cam_obj.keyframe_insert(data_path="location", frame=frame)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# Smooth camera interpolation
for fcurve in cam_obj.animation_data.action.fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'BEZIER'

# ===== RENDER SETTINGS =====
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.filepath = "C:/Users/0501JP/mmx/MMX_space_flight_15sec.mp4"

# Save animation blend
anim_blend = "C:/Users/0501JP/mmx/models/mmx_animation.blend"
bpy.ops.wm.save_as_mainfile(filepath=anim_blend)
print(f"Saved animation blend: {anim_blend}")

print("Animation setup complete. Ready to render.")
print(f"Frames: {scene.frame_start}-{scene.frame_end} ({scene.frame_end/scene.render.fps:.1f}s @ {scene.render.fps}fps)")
