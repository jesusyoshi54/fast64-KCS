# ------------------------------------------------------------------------
#    Header
# ------------------------------------------------------------------------
import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from pathlib import Path

from .kcs_gfx import import_geo_bin, export_geo_c
from .kcs_col import add_node, import_col_bin, export_col_c, set_camera_pathing, get_node_distance
from .kcs_utils import parse_stage_table, make_empty, find_item_from_iterable

from ..utility import PluginError, parentObject

# ------------------------------------------------------------------------
#    IO Operators
# ------------------------------------------------------------------------

# import a collision file / level block file
class KCS_Import_Col(Operator):
    bl_label = "Import Col Data"
    bl_idname = "kcs.import_col"
    bl_description = "Imports a level settings block to the currently selected Bank/ID pair. Level settings block imports are retrieved from the 'misc' folder in your selected folder"

    def execute(self, context: bpy.types.Context):
        scene = context.scene.KCS_scene
        bank_id = scene.import_bank_id.bank_id()
        file = Path(scene.decomp_path) / "assets" / "misc" / ("bank_%d" % bank_id[0]) / ("%d" % bank_id[1])
        if scene.file_format == "binary":
            name = file / "level.bin"
            if not name.exists():
                name = file / "misc.bin"
            if not name.exists():
                raise PluginError(f"Could not find file {name}, geo Bank/ID does not exist")
            import_col_bin(name, context, "KCS Col {}-{}".format(*bank_id))
        else:
            raise PluginError("C importing is not supported yet")
        return {"FINISHED"}


# import one gfx file
class KCS_Import_NLD_Gfx(Operator):
    bl_label = "Import Gfx Data"
    bl_idname = "kcs.import_nld_gfx"
    bl_description = "Imports a geo block to the currently selected Bank/ID pair. Geo block imports are retrieved from the 'geo' folder in your selected folder"

    def execute(self, context: bpy.types.Context):
        scene = context.scene.KCS_scene
        bank_id = scene.import_bank_id.bank_id()
        file = Path(scene.decomp_path) / "assets" / "geo" / ("bank_%d" % bank_id[0]) / ("%d" % bank_id[1])
        if scene.file_format == "binary":
            name = file / "geo.bin"
            if not name.exists():
                name = file / "block.bin"
            if not name.exists():
                raise PluginError(f"Could not find file {name}, geo Bank/ID does not exist")
            import_geo_bin(
                name, context, "KCS Gfx {}-{}".format(*bank_id), Path(scene.decomp_path) / "assets" / "image"
            )
        else:
            raise PluginError("C importing is not supported yet")
        return {"FINISHED"}


# import an entire stage (gfx, level block)
class KCS_Import_Stage(Operator):
    bl_label = "Import Stage"
    bl_idname = "kcs.import_stage"
    bl_description = "Imports a geo and level settings block to the currently selected stage. The target misc and geo Bank/IDs are retrieved from the main stage table in your selected folder"

    def execute(self, context: bpy.types.Context):
        scene = context.scene.KCS_scene
        stage_table = Path(scene.decomp_path) / "data" / "kirby.066630.2.c"  # this will probably change later
        stage = parse_stage_table(*scene.import_stage.stage, stage_table)

        gfx_bank, gfx_ID = [eval(a) for a in stage["geo"]]
        col_bank, col_ID = [eval(a) for a in stage["level_block"]]

        file_gfx = Path(scene.decomp_path) / "assets" / "geo" / (f"bank_{gfx_bank}") / (f"{gfx_ID}")
        file_col = Path(scene.decomp_path) / "assets" / "misc" / (f"bank_{col_bank}") / (f"{col_ID}")

        if scene.file_format == "binary":
            # import gfx
            name = file_gfx / "geo.bin"
            if not name.exists():
                name = file_gfx / "block.bin"
            if not name.exists():
                raise PluginError(f"Could not find file {name}, geo Bank/ID does not exist")
            import_geo_bin(
                name,
                context,
                "KCS Level {}-{}-{}".format(*scene.import_stage.stage),
                Path(scene.decomp_path) / "assets" / "image",
            )
            # import collision
            name = file_col / "level.bin"
            if not name.exists():
                name = file_col / "misc.bin"
            if not name.exists():
                raise PluginError(f"Could not find file {name}, misc Bank/ID selected is not a level")
            import_col_bin(name, context, "KCS Col {}-{}-{}".format(*scene.import_stage.stage))

        else:
            raise PluginError("C importing is not supported yet")
        return {"FINISHED"}


# export an area
class KCS_Export(Operator):
    bl_label = "Export Area"
    bl_idname = "kcs.export_area"
    bl_description = "Exports a geo and level settings block to the currently selected stage. The target misc and geo Bank/IDs are retrieved from the main stage table in your selected folder"

    def execute(self, context: bpy.types.Context):
        scene = context.scene.KCS_scene
        if scene.file_format == "binary":
            raise PluginError("Binary exports are not supported")

        stage_table = Path(scene.decomp_path) / "data" / "kirby.066630.2.c"  # this will probably change later
        stage = parse_stage_table(*scene.export_stage.stage, stage_table)

        gfx_bank, gfx_ID = [eval(a) for a in stage["geo"]]
        col_bank, col_ID = [eval(a) for a in stage["level_block"]]

        # need a KCS object
        level_obj = context.selected_objects[0]
        while level_obj:
            if not level_obj.KCS_obj.KCS_obj_type == "Level":
                level_obj = level_obj.parent
            else:
                break
        if not level_obj:
            raise PluginError('Obj is not Empty with type "Level"')

        geo_obj, col_obj = None, None

        for child in level_obj.children:
            if child.KCS_obj.KCS_obj_type == "Graphics":
                geo_obj = child
            if child.KCS_obj.KCS_obj_type == "Collision":
                col_obj = child

        if not col_obj:
            raise PluginError('Object with type "Collision" not a child of Level Root')
        if not geo_obj:
            raise PluginError('Object with type "Graphics" not a child of Level Root')

        # export geo
        file_gfx = Path(scene.decomp_path) / "assets" / "geo" / (f"bank_{gfx_bank}") / (f"{gfx_ID}")
        file_gfx.mkdir(exist_ok=True, parents=True)
        name = file_gfx / "geo"
        export_geo_c(name, geo_obj, context)

        # export col
        file_col = Path(scene.decomp_path) / "assets" / "misc" / (f"bank_{col_bank}") / (f"{col_ID}")
        file_col.mkdir(exist_ok=True, parents=True)
        name = file_col / "level"
        export_col_c(name, col_obj, context)

        level_obj.select_set(True)
        bpy.context.view_layer.objects.active = level_obj
        return {"FINISHED"}


# export a gfx file
class KCS_Export_Gfx(Operator):
    bl_label = "Export Gfx"
    bl_idname = "kcs.export_gfx"
    bl_description = "Exports a geo block to the currently selected Bank/ID pair. Geo block exports goes into the 'geo' folder in your selected folder"

    def execute(self, context: bpy.types.Context):
        scene = context.scene.KCS_scene
        if scene.file_format == "binary":
            raise PluginError("Binary exports are not supported")
        # need a KCS object
        obj = context.selected_objects[0]
        while obj:
            if not obj.KCS_obj.KCS_obj_type == "Graphics":
                obj = obj.parent
            else:
                break
        if not obj:
            raise PluginError('Obj is not Empty with type "Graphics"')

        bank_id = scene.export_bank_id.bank_id()
        file = Path(scene.decomp_path) / "assets" / "geo" / (f"bank_{bank_id[0]}") / (f"{bank_id[1]}")
        file.mkdir(exist_ok=True, parents=True)
        name = file / "geo"
        export_geo_c(name, obj, context)
        return {"FINISHED"}


# export a misc file
class KCS_Export_Col(Operator):
    bl_label = "Export Col"
    bl_idname = "kcs.export_col"
    bl_description = "Exports a level settings block to the currently selected Bank/ID pair. Level settings block exports goes into the 'misc' folder in your selected folder"

    def execute(self, context: bpy.types.Context):
        scene = context.scene.KCS_scene
        if scene.file_format == "binary":
            raise PluginError("Binary exports are not supported")
        # need a KCS object
        obj = context.selected_objects[0]
        while obj:
            if not obj.KCS_obj.KCS_obj_type == "Collision":
                obj = obj.parent
            else:
                break
        if not obj:
            raise PluginError('Obj is not Empty with type "Collision"')
        bank_id = scene.export_bank_id.bank_id()
        file = Path(scene.decomp_path) / "assets" / "misc" / (f"bank_{bank_id[0]}") / (f"{bank_id[1]}")
        file.mkdir(exist_ok=True, parents=True)
        name = file / "level"
        export_col_c(name, obj, context)
        return {"FINISHED"}


# ------------------------------------------------------------------------
#    Helper Operators
# ------------------------------------------------------------------------

# these operators are added to panels to make things easier for the users
# their purpose is to aid in level creation

# adds a level empty with the hierarchy setup needed to have one basic node
class KCS_Add_Level(Operator):
    bl_label = "Add Level Empty"
    bl_idname = "kcs.add_kcslevel"
    bl_description = "Adds a level root object with collision and graphics children properly setup, and adds a single node to the collision root"

    def execute(self, context: bpy.types.Context):
        collection = bpy.context.scene.collection
        Lvl = make_empty("KCS Level Rt", "PLAIN_AXES", collection)
        Lvl.KCS_obj.KCS_obj_type = "Level"
        Col = make_empty("KCS Level Col", "PLAIN_AXES", collection)
        Col.KCS_obj.KCS_obj_type = "Collision"
        parentObject(Lvl, Col, 0)
        Gfx = make_empty("KCS Level Gfx", "PLAIN_AXES", collection)
        Gfx.KCS_obj.KCS_obj_type = "Graphics"
        parentObject(Lvl, Gfx, 0)
        # Make Node
        PathData = bpy.data.curves.new("KCS Path Node", "CURVE")
        PathData.splines.new("POLY")
        PathData.splines[0].points.add(4)
        for i, s in enumerate(PathData.splines[0].points):
            s.co = (i - 2, 0, 0, 0)
        Node = bpy.data.objects.new("KCS Node", PathData)
        collection.objects.link(Node)
        parentObject(Col, Node, 0)
        # make camera
        CamDat = bpy.data.cameras.new("KCS Node Cam")
        CamObj = bpy.data.objects.new("KCS Node Cam", CamDat)
        collection.objects.link(CamObj)
        parentObject(Node, CamObj, 0)
        # Make Camera Volume
        Vol = make_empty("KCS Cam Volume", "CUBE", collection)
        Vol.KCS_obj.KCS_obj_type = "Camera Volume"
        parentObject(CamObj, Vol, 0)
        Lvl.select_set(True)
        return {"FINISHED"}


# adds a node to the collision parent
class KCS_Add_Node(Operator):
    bl_label = "Add Node"
    bl_idname = "kcs.add_kcsnode"
    bl_description = "Adds a new node as a child to the current collision root object"

    def execute(self, context: bpy.types.Context):
        Rt = context.object
        collection = context.object.users_collection[0]
        add_node(Rt, collection)
        return {"FINISHED"}


# adds animation to cameras to follow paths
class KCS_Animate_Nodes(Operator):
    bl_label = "Animate Camera"
    bl_idname = "kcs.anim_camera"
    bl_description = "Animates all camera starting at the root node, and then sets scene rendering properties for the most accurate preview possible with current kirby and n64 knowledge. Subject to improvements"

    def execute(self, context: bpy.types.Context):
        col_root = context.object
        max_frame = 0
        for child in col_root.children:
            if child.type == "CURVE":
                camera = find_item_from_iterable(child.children, "type", "CAMERA")
                node_distance = get_node_distance(child.data.KCS_node.node_num, col_root, context.scene.KCS_scene.scale)
                if node_distance:
                    frame_start = int(node_distance[1])
                    resolve_time = int(node_distance[0].node_length)
                    if frame_start + resolve_time > max_frame:
                        max_frame = frame_start + resolve_time
                        context.scene.frame_end = max_frame
                    set_camera_pathing(camera, child, frame_start=frame_start, resolve_time=resolve_time)
        # set rendering properties to fit kirby
        context.scene.render.engine = "BLENDER_EEVEE" # speed
        context.scene.eevee.taa_render_samples = 16 # speed
        context.scene.view_settings.view_transform = "Standard"
        context.scene.sequencer_colorspace_settings.name = "sRGB"
        context.scene.view_settings.exposure = 0
        context.scene.view_settings.gamma = 1
        context.scene.frame_start = 0
        context.scene.render.resolution_x = 300
        context.scene.render.resolution_y = 172
        context.scene.render.fps = 30
        context.scene.render.film_transparent = True
        context.scene.render.image_settings.file_format = "FFMPEG"
        bpy.ops.script.python_file_run(filepath="C:\\Program Files\\Blender Foundation\\Blender 3.2\\3.2\\scripts\\presets\\ffmpeg\\WebM_(VP9+Opus).py") # webm output preset
        return {"FINISHED"}


# adds an entity to the collision parent
class KCS_Add_Ent(Operator):
    bl_label = "Add Entity"
    bl_idname = "kcs.add_kcsent"
    bl_description = "Adds a single entity as a child of the current node"

    def execute(self, context: bpy.types.Context):
        node = context.object.data.KCS_node
        obj = bpy.data.objects.new(f"Entity {node.node_num}", None)
        collection = context.object.users_collection[0]
        collection.objects.link(obj)
        obj.KCS_obj.KCS_obj_type = "Entity"
        parentObject(context.object, obj, 0)
        obj.location = context.object.data.splines[0].points[0].co.xyz + context.object.location
        return {"FINISHED"}


# adds a texture to the current texture scroll
class KCS_Add_Tex(Operator):
    bl_label = "Add Texture"
    bl_idname = "kcs.add_tex"

    def execute(self, context: bpy.types.Context):
        mat = context.material
        scr = mat.KCS_tx_scroll
        scr.Textures.add()
        return {"FINISHED"}


# adds a palette to the current texture scroll
class KCS_Add_Pal(Operator):
    bl_label = "Add Palette"
    bl_idname = "kcs.add_pal"

    def execute(self, context: bpy.types.Context):
        mat = context.material
        scr = mat.KCS_tx_scroll
        scr.Palettes.add()
        return {"FINISHED"}


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------


kcs_operators = (
    KCS_Export,
    KCS_Export_Gfx,
    KCS_Export_Col,
    KCS_Import_Stage,
    KCS_Add_Level,
    KCS_Add_Ent,
    KCS_Add_Node,
    KCS_Animate_Nodes,
    KCS_Import_NLD_Gfx,
    KCS_Import_Col,
    KCS_Add_Tex,
    KCS_Add_Pal,
)


def kcs_operator_register():
    for cls in kcs_operators:
        register_class(cls)


def kcs_operator_unregister():
    for cls in reversed(kcs_operators):
        unregister_class(cls)
