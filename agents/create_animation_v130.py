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
scene.frame_end = 300  # 10 seconds @ 30 fps (better for orbital view)

# Clear animation
bpy.ops.object.select_all(action='SELECT')
for obj in bpy.context.selected_objects:
    obj.animation_data_clear()
bpy.ops.object.select_all(action='DESELECT')

# Camera - WIDER LENS, FURTHER DISTANCE (v1.3.0 camera fix)
cam_data = bpy.data.cameras.new('AnimCamera')
cam_obj = bpy.data.objects.new('AnimCamera', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 28.0  # Wider (was 35mm)
cam_data.clip_start = 0.1
cam_data.clip_end = 1000

# World: Bright space (keep v1.2.0 lighting)
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
bg.inputs['Strength'].default_value = 0.5

# Lighting (keep v1.2.0 values)
sun_data = bpy.data.lights.new('Sun', 'SUN')
sun_obj = bpy.data.objects.new('Sun', sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = Euler((math.radians(45), math.radians(30), 0), 'XYZ')
sun_data.energy = 15.0
sun_data.color = (1.0, 0.95, 0.9)
sun_data.angle = 0.53

fill_data = bpy.data.lights.new('Fill', 'SUN')
fill_obj = bpy.data.objects.new('Fill', fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = Euler((math.radians(-45), math.radians(-30), 0), 'XYZ')
fill_data.energy = 3.0
fill_data.color = (0.3, 0.4, 0.6)

rim_data = bpy.data.lights.new('Rim', 'SUN')
rim_obj = bpy.data.objects.new('Rim', rim_data)
scene.collection.objects.link(rim_obj)
rim_obj.rotation_euler = Euler((math.radians(180), 0, 0), 'XYZ')
rim_data.energy = 2.0
rim_data.color = (0.2, 0.3, 0.5)

# MMX animation - slower, more graceful flight
mmx_obj.location = (0, 0, 0)
mmx_obj.rotation_euler = Euler((0, 0, 0), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=1)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=1)

mmx_obj.location = (3, -15, 2)
mmx_obj.rotation_euler = Euler((math.radians(3), math.radians(5), math.radians(2)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=100)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=100)

mmx_obj.location = (8, -35, 5)
mmx_obj.rotation_euler = Euler((math.radians(-1), math.radians(12), math.radians(-3)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=200)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=200)

mmx_obj.location = (15, -60, 8)
mmx_obj.rotation_euler = Euler((math.radians(5), math.radians(20), math.radians(3)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=300)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=300)

# Camera: PULL BACK - orbit distance 45 (was 25), 1 orbit (was 2), slower
cam_distance = 45.0   # v1.3.0: pulled back from 25
cam_height = 12.0
orbits = 1.0          # v1.3.0: reduced from 2.0
for frame in range(1, 301, 3):
    scene.frame_set(frame)
    mmx_loc = mmx_obj.matrix_world.translation
    orbit_angle = (frame - 1) * (2 * math.pi / 300) * orbits
    cam_x = mmx_loc.x + cam_distance * math.sin(orbit_angle)
    cam_y = mmx_loc.y + cam_distance * math.cos(orbit_angle) - 20.0
    cam_z = mmx_loc.z + cam_height + 8.0 * math.sin(orbit_angle * 1.2)
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
scene.render.resolution_x = 1920  # Higher res for quality
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "C:/Users/0501JP/mmx/tmp/renders_v130/frame_"

# Save v1.3.0 blend
anim_blend = "C:/Users/0501JP/mmx/models/mmx_animation_v130.blend"
bpy.ops.wm.save_as_mainfile(filepath=anim_blend)
print(f"Saved v1.3.0: {anim_blend}")
print(f"Frames: 1-300 (10 sec @ 30fps)")
print(f"Camera: lens=28mm, distance=45, orbits=1.0")
print(f"Lighting: sun=15, fill=3, rim=2, world=0.5")
