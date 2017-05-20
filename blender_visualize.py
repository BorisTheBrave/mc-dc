"""Utility for invoking blender and rending .obj files"""

import subprocess
import os
import tempfile

blender_bin = r"C:\Program Files\Blender Foundation\Blender\blender.exe"
assert os.path.exists(blender_bin)

deg_to_rad = 0.017453292523928

def blender_render(obj_file, output_render):
        # Create Blender script for scene we want to render
        script = ""
        camera = (5.95839, -2.64368, 3.245561), (63.524*deg_to_rad,0.76*deg_to_rad,65.791*deg_to_rad)
        # Marshall arguments into blender
        script += "obj_file = {0}\n".format(repr(os.path.abspath(obj_file)))
        script += "output_render = {0}\n".format(repr(os.path.abspath(output_render)))
        script += "camera_location = {0}\n".format(repr(camera[0]))
        script += "camera_rotation = {0}\n".format(repr(camera[1]))
        # Setup the scene and render it
        script += """def doit():
        import bpy
        # Import obj
        bpy.ops.scene.new(type='EMPTY')
        bpy.ops.import_scene.obj("EXEC_DEFAULT", filepath=obj_file)
        orig_mesh = bpy.context.scene.objects[0]

        # Setup wireframe
        bpy.context.scene.objects.active = orig_mesh
        bpy.ops.object.duplicate()
        bpy.ops.object.modifier_add(type='WIREFRAME')
        material = bpy.data.materials.new("red")
        material.diffuse_color = (1.0, 0, 0)
        material.use_shadeless = True
        bpy.context.active_object.data.materials.append(material)
        bpy.context.scene.objects.active.parent = orig_mesh

        # Setup vertices
        bpy.context.scene.objects.active = orig_mesh
        bpy.ops.object.particle_system_add()
        particle_settings = bpy.data.particles["ParticleSettings"]
        particle_settings.emit_from = 'VERT'
        particle_settings.show_unborn = True
        particle_settings.use_emit_random = False
        particle_settings.render_type = 'OBJECT'
        particle_settings.physics_type = 'NO'
        bpy.ops.mesh.primitive_ico_sphere_add(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
        psphere = bpy.context.scene.objects.active
        particle_settings.dupli_object = psphere
        psphere.data.materials.append(material)

        # Setup lighting
        bpy.ops.object.lamp_add(type='POINT', radius=5, location=(5.7, 0.5, 3.5))

        # Setup world
        my_world = bpy.data.worlds.new("world")
        bpy.context.scene.world = my_world
        bpy.context.scene.world.light_settings.use_environment_light = True

        # Setup animation
        bpy.context.scene.objects.active = orig_mesh
        #bpy.context.area.type = 'VIEW_3D'
        #bpy.context.space_data.context = 'OBJECT'
        orig_mesh.keyframe_insert('rotation_euler',group="Rot")
        bpy.context.scene.frame_end = 25
        bpy.context.scene.frame_current = 101
        bpy.context.object.rotation_euler[2] = 6.28319
        orig_mesh.keyframe_insert('rotation_euler',group="Rot")
        curve = bpy.data.actions[0].fcurves[2]
        curve.keyframe_points[0].interpolation = 'LINEAR'
        curve.keyframe_points[1].interpolation = 'LINEAR'


        # Setup camera and render
        bpy.ops.object.camera_add(location=camera_location,rotation=camera_rotation)
        bpy.context.active_object.data.clip_end = 250
        bpy.context.scene.camera = bpy.context.active_object
        bpy.context.scene.render.filepath = output_render
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.render.resolution_x = 400
        bpy.context.scene.render.resolution_y = 400
        bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

        # Actually render
        bpy.ops.render.render(write_still=True)

        # Exerimental animation support
        bpy.data.scenes[1].render.image_settings.file_format = 'H264'
        bpy.ops.render.render(animation=True)
        """.strip()+"\n\n"
        script +="doit()\n"
        with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(script.encode("utf-8"))
        args = [blender_bin,"-P",f.name]
        if True:
            # Start blender in "background mode"
            args.insert(1, "-b")
        subprocess.check_call(args)

if __name__=="__main__":
    blender_render("output.obj", "example.png")