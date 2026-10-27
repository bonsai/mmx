import bpy, os, math
from mathutils import Vector, Euler

blend_file = "C:/Users/0501JP/mmx/models/mmx_colored_lowpoly.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

mmx_obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 16
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 150  # 5 seconds @ 30 fps

# Clear animation
bpy.ops.object.select_all(action='SELECT')
for obj in bpy.context.selected_objects:
    obj.animation_data_clear()
bpy.ops.object.select_all(action='DESELECT')

# Camera
cam_data = bpy.data.cameras.new('AnimCamera')
cam_obj = bpy.data.objects.new('AnimCamera', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 35
cam_data.clip_start = 0.1
cam_data.clip_end = 1000

# World: Bright space
world = bpy.data.worlds.new("SpaceWorld")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes): nodes.remove(n)
bg = nodes.new('ShaderNodeBackground')
bg.location = (0, 0)
tex_coord = nodes.new('ShaderNodeTexCoord')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 200
noise.inputs['Detail'].default_value = 8
noise.inputs['Roughness'].default_value = 0.7
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].position = 0.92
color_ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1)
color_ramp.color_ramp.elements[1].position = 0.97
color_ramp.color_ramp.elements[1].color = (1, 0.98, 0.9, 1)
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'
mix.inputs['Fac'].default_value = 1.0
mix.inputs[1].default_value = (0.02, 0.02, 0.03, 1)
mix.inputs[2].default_value = (1, 0.98, 0.9, 1)
output = nodes.new('ShaderNodeOutputWorld')
links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], mix.inputs['Color2'])
links.new(mix.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 0.5  # Brighter stars

# STRONG Lighting - VLM feedback
sun_data = bpy.data.lights.new('Sun', 'SUN')
sun_obj = bpy.data.objects.new('Sun', sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = Euler((math.radians(45), math.radians(30), 0), 'XYZ')
sun_data.energy = 15.0  # 3x brighter
sun_data.color = (1.0, 0.95, 0.9)
sun_data.angle = 0.53

# Fill light
fill_data = bpy.data.lights.new('Fill', 'SUN')
fill_obj = bpy.data.objects.new('Fill', fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = Euler((math.radians(-45), math.radians(-30), 0), 'XYZ')
fill_data.energy = 3.0  # 6x brighter
fill_data.color = (0.3, 0.4, 0.6)

# Rim light for shape definition
rim_data = bpy.data.lights.new('Rim', 'SUN')
rim_obj = bpy.data.objects.new('Rim', rim_data)
scene.collection.objects.link(rim_obj)
rim_obj.rotation_euler = Euler((math.radians(180), 0, 0), 'XYZ')
rim_data.energy = 2.0
rim_data.color = (0.2, 0.3, 0.5)

# MMX animation - fly through space
mmx_obj.location = (0, 0, 0)
mmx_obj.rotation_euler = Euler((0, 0, 0), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=1)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=1)

mmx_obj.location = (5, -20, 3)
mmx_obj.rotation_euler = Euler((math.radians(5), math.radians(10), math.radians(3)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=50)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=50)

mmx_obj.location = (12, -45, 8)
mmx_obj.rotation_euler = Euler((math.radians(-2), math.radians(20), math.radians(-5)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=100)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=100)

mmx_obj.location = (20, -75, 12)
mmx_obj.rotation_euler = Euler((math.radians(8), math.radians(30), math.radians(5)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=150)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=150)

# Camera: orbit around MMX
cam_distance = 25
cam_height = 8
for frame in range(1, 151, 3):
    scene.frame_set(frame)
    mmx_loc = mmx_obj.matrix_world.translation
    orbit_angle = (frame - 1) * (2 * math.pi / 150) * 2.0  # 2 orbits in 5 sec
    cam_x = mmx_loc.x + cam_distance * math.sin(orbit_angle)
    cam_y = mmx_loc.y + cam_distance * math.cos(orbit_angle) - 15
    cam_z = mmx_loc.z + cam_height + 5 * math.sin(orbit_angle * 1.5)
    cam_obj.location = (cam_x, cam_y, cam_z)
    direction = mmx_loc - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.keyframe_insert(data_path="location", frame=frame)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# Bezier interpolation
def set_bezier(obj):
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for kf in fc.keyframe_points:
                            kf.interpolation = 'BEZIER'

set_bezier(mmx_obj)
set_bezier(cam_obj)

# Render settings
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "C:/Users/0501JP/mmx/renders5/frame_"

# Save
anim_blend = "C:/Users/0501JP/mmx/models/mmx_animation_5sec.blend"
bpy.ops.wm.save_as_mainfile(filepath=anim_blend)
print(f"Saved: {anim_blend}")
print("Frames: 1-150 (5 sec @ 30fps)")
