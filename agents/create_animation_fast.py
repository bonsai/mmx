import bpy, os, math
from mathutils import Vector, Euler

blend_file = "C:/Users/0501JP/mmx/models/mmx_lowpoly.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

mmx_obj = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'MMX' in obj.name:
        mmx_obj = obj
        break
if not mmx_obj:
    mmx_obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'  # Eevee for fast render
scene.eevee.taa_render_samples = 16
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 450

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

# World: Space (Eevee compatible)
world = bpy.data.worlds.new("SpaceWorld")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)
bg = nodes.new('ShaderNodeBackground')
bg.inputs[0].default_value = (0.01, 0.01, 0.02, 1.0)
bg.inputs[1].default_value = 0.2
tex_coord = nodes.new('ShaderNodeTexCoord')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 200
noise.inputs['Detail'].default_value = 8
noise.inputs['Roughness'].default_value = 0.7
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].position = 0.95
color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
color_ramp.color_ramp.elements[1].position = 0.98
color_ramp.color_ramp.elements[1].color = (1, 1, 0.9, 1)
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'
mix.inputs['Fac'].default_value = 1.0
mix.inputs[1].default_value = (0.01, 0.01, 0.02, 1.0)
mix.inputs[2].default_value = (1, 1, 0.9, 1)
output = nodes.new('ShaderNodeOutputWorld')
links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], mix.inputs['Color2'])
links.new(mix.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])

# Lighting
sun_data = bpy.data.lights.new('Sun', 'SUN')
sun_obj = bpy.data.objects.new('Sun', sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = Euler((math.radians(45), math.radians(30), 0), 'XYZ')
sun_data.energy = 5.0
sun_data.color = (1.0, 0.95, 0.9)

# MMX animation
mmx_obj.location = (0, 0, 0)
mmx_obj.rotation_euler = Euler((0, 0, 0), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=1)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=1)
mmx_obj.location = (10, -30, 5)
mmx_obj.rotation_euler = Euler((math.radians(10), math.radians(15), math.radians(5)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=150)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=150)
mmx_obj.location = (25, -70, 12)
mmx_obj.rotation_euler = Euler((math.radians(-5), math.radians(30), math.radians(-10)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=300)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=300)
mmx_obj.location = (40, -120, 20)
mmx_obj.rotation_euler = Euler((math.radians(15), math.radians(45), math.radians(8)), 'XYZ')
mmx_obj.keyframe_insert(data_path="location", frame=450)
mmx_obj.keyframe_insert(data_path="rotation_euler", frame=450)

# Camera animation
cam_distance = 30
cam_height = 12
for frame in range(1, 451, 5):
    scene.frame_set(frame)
    mmx_loc = mmx_obj.matrix_world.translation
    orbit_angle = (frame - 1) * (2 * math.pi / 450) * 2.5
    cam_x = mmx_loc.x + cam_distance * math.sin(orbit_angle)
    cam_y = mmx_loc.y + cam_distance * math.cos(orbit_angle) - 20
    cam_z = mmx_loc.z + cam_height + 8 * math.sin(orbit_angle * 1.5)
    cam_obj.location = (cam_x, cam_y, cam_z)
    direction = mmx_loc - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.keyframe_insert(data_path="location", frame=frame)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# Set Bezier interpolation
def set_bezier_interpolation(obj):
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for kf in fc.keyframe_points:
                            kf.interpolation = 'BEZIER'

set_bezier_interpolation(mmx_obj)
set_bezier_interpolation(cam_obj)

# Render settings - PNG sequence
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = "C:/Users/0501JP/mmx/renders/frame_"

# Save
anim_blend = "C:/Users/0501JP/mmx/models/mmx_animation_eevee.blend"
bpy.ops.wm.save_as_mainfile(filepath=anim_blend)
print(f"Saved: {anim_blend}")
print("Eevee render - much faster!")
