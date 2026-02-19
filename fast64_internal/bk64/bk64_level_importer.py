from __future__ import annotations

import bpy
import bmesh

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
    IntVectorProperty,
    BoolVectorProperty,
)
from bpy.types import (
    Panel,
    Menu,
    Operator,
    PropertyGroup,
)
from bpy.utils import register_class, unregister_class
from mathutils import Vector, Euler, Matrix, Quaternion

import os, sys, struct, shutil, math, re
from pathlib import Path
from collections import namedtuple
from dataclasses import dataclass, field
from typing import TextIO, BinaryIO
from collections.abc import Sequence

from ..f3d.f3d_import import *
from ..utility_importer import *
from ..utility import parentObject
from ..panels import BK64_Panel

# -------------------------------------------------------------------------------
#    Classes
# -------------------------------------------------------------------------------

@dataclass
class MapModelDescription:
    map_id: int
    opa_model_id: int
    xlu_model_id: int
    min_bounds: tuple
    max_bounds: tuple
    scale: float

    def get_opa_asset_num(self):
        return re.search("ASSET_[0-9A-Fa-f]+?_", self.opa_model_id).group()[6:-1]

    def get_xlu_asset_num(self):
        return re.search("ASSET_[0-9A-Fa-f]+?_", self.xlu_model_id).group()[6:-1]


# necessary?
class Vertices():
    _Vec3 = namedtuple("Vec3", "x y z")
    _UV = namedtuple("UV", "s t")
    _color = namedtuple("rgba", "r g b a")

    def __init__(self):
        self.UVs = []
        self.VCs = []
        self.Pos = []

    def _make(self, v):
        self.Pos.append(self._Vec3._make(v[0:3]))
        self.UVs.append(self._UV._make(v[4:6]))
        self.VCs.append(self._color._make(v[6:10]))

    # has a little bit of special formatting so it uses its own method
    def write(self, file):
        self.add_header_data(f"Vtx Geo_Vertices[{len(self.Pos)}]", static=True)
        file.write(f"static Vtx Geo_Vertices[{len(self.Pos)}] = {{\n")

        def spc(x):
            return "{" + ", ".join([hex(a) for a in x]) + "}"

        for position, uv, colorOrNormal in zip(self.Pos, self.UVs, self.VCs):
            line = (
                "{{ "
                + ", ".join([spc(position), "0", spc(uv), spc(colorOrNormal)])
                + " }}"
            )
            file.write(f"\t{line},\n")
        file.write("};\n\n")


class GeoLayout(DataParser, BinWrite):
    # just overrides the default arg make_str for the base class
    def unpack_type(
        self,
        offset: int,
        unpack_str: Union[PackedFormat, str],
        ret_iterable=False,
        make_str: bool = False,
    ):
        return super().unpack_type(self.bin_file, offset, unpack_str, ret_iterable, make_str)

    def __init__(self, start: int, bin_file: BinaryIO):
        self.bin_file = bin_file
        self.child_geo_offset = None
        self.child_geos: list[GeoLayout] = []
        cmd_type, cmd_len = self.unpack_type(start, ">2L")
        func = getattr(self, f"cmd_{cmd_type}")
        if not func:
            print(cmd_type, cmd_len)
            raise "no geo cmd found"
        self.length = func(start + 4)

    # put cmd in blender world
    def parse_cmd(self, root: bpy.types.Object):
        geo_obj = bpy.data.objects.new("Empty", None)
        parentObject(root, geo_obj)
        geo_obj.fast64.bk64.geo_type = self.data.cmd_name
        geo_obj.fast64.bk64.geo_args = self.dataclass_str(self.data)
        return geo_obj

    @dataclass
    class _cmd_sort:
        cmd_name: str
        size: int
        child1_co: tuple[float]
        child2_co: tuple[float]
        flag: int
        child1_off: int
        child2_off: int

    def cmd_1(self, start: int):
        data = self.unpack_type(start, ">L6fH2L")
        self.data = self._cmd_sort("CMD_SORT", data[0], data[1:4], data[4:7], *data[7:])
        return data[0]

    @dataclass
    class _cmd_bone:
        cmd_name: str
        dl_offset: int
        cmd_len: int
        bone_id: int
        unk_0A: int

    def cmd_2(self, start: int):
        data = self.unpack_type(start, ">L2BH")
        self.data = self._cmd_bone("CMD_BONE", *data)
        return data[1] * 0x10

    @dataclass
    class _cmd_load_dl:
        cmd_name: str
        size: int
        dl_offset: int
        tri_cnt: int

    def cmd_3(self, start: int):
        data = self.unpack_type(start, ">L2H")
        self.data = self._cmd_load_dl("CMD_LOAD_DL", *data)
        return data[0]

    @dataclass
    class _cmd_skinning:
        cmd_name: str
        size: int
        prev_bone: int
        dl_offsets: list[int]

    def cmd_5(self, start: int):
        data = self.unpack_type(start, ">LH")
        self.data = self._cmd_skinning(
            "CMD_SKINNING",
            *data,
            self.unpack_type(start + 10, f">{(data[0]-10) // 2}H"),
        )
        return data[0]

    @dataclass
    class _cmd_branch:
        cmd_name: str
        size: int
        target: int

    def cmd_6(self, start: int):
        data = self.unpack_type(start, ">2L")
        self.data = self._cmd_branch("CMD_BRANCH", *data)
        return data[0]

    @dataclass
    class _cmd_lod:
        cmd_name: str
        size: int
        max_dst: float
        min_dst: float
        test_pos: tuple[float]
        get_offset: int

    def cmd_8(self, start: int):
        data = self.unpack_type(start, ">L5fL")
        self.data = self._cmd_lod("CMD_LOD", *data[0:3], data[3:6], data[6])
        return data[0]

    @dataclass
    class _cmd_ref_pth:
        cmd_name: str
        size: int
        ref_pt_index: int
        bone_index: int
        bone_offset: tuple[float]

    def cmd_10(self, start: int):
        data = self.unpack_type(start, ">L2H3f")
        self.data = self._cmd_ref_pth("CMD_REF_PATH", *data[0:3], *data[3:6])
        return data[0]

    @dataclass
    class _cmd_switch:
        cmd_name: str
        size: int
        child_cnt: int
        switch_index: int
        geo_offsets: tuple[int]

    def cmd_12(self, start: int):
        data = self.unpack_type(start, ">L2H")
        if data[0]:
            self.data = self._cmd_switch(
                "CMD_SWITCH",
                *data,
                self.unpack_type(start + 8, f">{(data[0]-8) // 4}L"),
            )
        else:
            self.data = self._cmd_switch("CMD_SWITCH", *data, [])
        return data[0]

    @dataclass
    class _cmd_draw_dst:
        cmd_name: str
        size: int
        neg_crds: tuple[int]
        pos_crds: tuple[int]
        unk14: int

    def cmd_13(self, start: int):
        data = self.unpack_type(start, ">L6h2H")
        self.data = self._cmd_draw_dst(
            "CMD_DRAW_DISTANCE", data[0], data[1:4], data[4:7], data[7]
        )
        if data[7]:
            self.child_geo_offset = data[7]
        return data[0]

    @dataclass
    class _cmd_unk_14:
        cmd_name: str
        size: int
        neg_crds: tuple[int]
        pos_crds: tuple[int]
        pad: int
        child_cmds: tuple[int]

    def cmd_14(self, start: int):
        data = self.unpack_type(start, ">L6hL")
        self.data = self._cmd_switch(
            "CMD_UNK_0E",
            *data[:8],
            self.unpack_type(start + 20, f">{(data[0]-20) // 4}L"),
        )
        return data[0]

    @dataclass
    class _cmd_unk_15:
        cmd_name: str
        size: int
        unk8: int
        unkA: int
        unkB: int
        unkC: list[int]

    def cmd_15(self, start: int):
        data = self.unpack_type(start, ">Lh14B")
        self.data = self._cmd_unk_15("CMD_UNK_0F", *data[:4], data[4:])
        if data[1]:
            self.child_geo_offset = data[1]
        return data[0]


# I used just regular format strings instead of PackedFormat classes because I was lazy
# but it probably doesn't affect the overall result
class ModelBin(DataParser):
    # just overrides the default arg make_str for the base class
    def unpack_type(
        self,
        offset: int,
        unpack_str: Union[PackedFormat, str],
        ret_iterable=False,
        make_str: bool = False,
    ):
        return super().unpack_type(self.bin_file, offset, unpack_str, ret_iterable, make_str)

    @dataclass
    class _header:
        start: int
        geo_offset: int
        tex_list: int
        geo_type: int
        dl_list: int
        vtx_list: int
        unk_hitboxes: int
        anim_list: int
        col_list: int
        unk20_list: int  # contains camera boundary boxes
        fx_list: int
        unk28: int
        anim_tex_list: int

        type_name = "BKModelBin"

    @dataclass
    class _tex_header:
        size: int
        tex_cnt: int
        pad: int
        type_name = "TexHeader"

    @dataclass
    class _meta_tex:
        tex_offset: int
        tex_type: int
        pad1: int
        width: int
        height: int
        pad2: int
        pad3: int

    @dataclass
    class _vtx_header:
        min_co: int
        max_co: int
        center_co: int
        dst_center: int
        vtx_cnt: int
        dst_origin: int

        type_name = "VtxHeader"

    # key - offset, val - (str_type, unpack_str, callable <optional>)
    _vtx_header_unpack = {
        0x00: ("s16[3]", ">3h", None),
        0x06: ("s16[3]", ">3h", None),
        0x0C: ("s16[3]", ">3h", None),
        0x12: ("s16", ">h", None),
        0x14: ("u16", ">H", None),
        0x16: ("s16", ">h", None),
    }

    @dataclass
    class _col_header:
        min_co: int
        max_co: int
        y_stride: int
        z_stride: int
        num_cubes: int
        cube_scale: int
        num_tris: int
        pad: int
        type_name = "ColHeader"

    _col_header_unpack = {
        0x00: ("s16[3]", ">3h", None),
        0x06: ("s16[3]", ">3h", None),
        0x0C: ("u16", ">H", None),
        0x0E: ("u16", ">H", None),
        0x10: ("u16", ">H", None),
        0x12: ("u16", ">H", None),
        0x14: ("u16", ">H", None),
        0x16: ("u16", ">H", None),
    }

    @dataclass
    class _geo_cube:
        tri_id: int
        tri_cnt: int

    @dataclass
    class _col_tri:
        v1: int
        v2: int
        v3: int
        unk: int
        col_flags: int

    @dataclass
    class _fx_dat:
        dat_start: int
        vtx_cnt: int
        vtx_refs: int

    @dataclass
    class _geo_data:
        cmd_type: int
        cmd_data: list[int | float]

    def __init__(self, bin_file, ptr=None):
        self.bin_file = bin_file
        self.ptrs = ptr
        self.header = []
        self.child_symbols = []
        self.symbols = dict()
        self.main_header = self._header(*self.unpack_type(0, ">2L2h9L"))
        self.get_tex_list()
        self.get_dl_list()
        self.get_vtx_list()
        self.get_col_list()
        self.get_fx_list()
        self.get_geo_layout()
        self.f3d = DL(parse_target = DataParser._binary_parsing)
        self.f3d.bin_file = self.bin_file
        self.f3d.banks = BankLoads()
        self.get_banks()

    def get_banks(self):
        # seg 1 is verts, seg 2 textures, seg 3 render mode table, seg 11-15 animated textures
        banks = self.f3d.banks
        banks.tlb[0x01] = [self.main_header.vtx_list, len(self.bin_file)]
        banks.tlb[0x02] = [self.main_header.tex_list, len(self.bin_file)]
        # this is inside the ROM somewhere... which means it is in C code
        # banks.tlb[0x03] = [start,end]


    def get_tex_list(self):
        self.tex_header = self._tex_header(
            *self.unpack_type(self.main_header.tex_list, ">L2H", make_str=False)
        )
        # tex data offset is offset from tex_data section start
        self.meta_tex_data = []
        for i in range(self.tex_header.tex_cnt):
            data = self._meta_tex(
                *self.unpack_type(
                    8 + self.main_header.tex_list + i * 0x10, ">LHHBBLH", make_str=False
                )
            )
            self.meta_tex_data.append(data)
        self.tex_data_start = (
            self.tex_header.tex_cnt * 0x10 + 8 + self.main_header.tex_list
        )
        # extract textures I guess

    def get_dl_list(self):
        start = self.main_header.dl_list
        self.dl_cmd_cnt = self.unpack_type(start, ">L")
        self.dl_cmds = []
        for i in range(self.dl_cmd_cnt):
            self.dl_cmds.append(self.bin_file[start + i * 8 : start + i * 8 + 8])

    def get_vtx_list(self):
        self.vtx_header = self._vtx_header(
            *self.extract_dict(self.main_header.vtx_list, self._vtx_header_unpack)
        )
        self.vertices = Vertices()
        for i in range(self.vtx_header.vtx_cnt // 2):
            pos = self.main_header.vtx_list + 0x18 + i * 0x10
            self.vertices._make(self.unpack_type(pos, ">6h4B"))

    def get_col_list(self):
        self.col_header = self._col_header(
            *self.extract_dict(self.main_header.col_list, self._col_header_unpack)
        )
        self.geo_cubes = []
        self.col_tris = []
        for i in range(self.col_header.num_cubes):
            pos = self.main_header.col_list + 0x18 + i * 0x04
            self.geo_cubes.append(self._geo_cube(*self.unpack_type(pos, ">2H")))

        col_tri_start = (
            self.main_header.col_list + 0x18 + self.col_header.num_cubes * 0x04
        )
        for i in range(self.col_header.num_tris):
            pos = col_tri_start + i * 0x0C
            self.col_tris.append(self._col_tri(*self.unpack_type(pos, ">4HL")))

    def get_fx_list(self):
        self.fx_cnt = self.unpack_type(self.main_header.fx_list, ">H")
        offset = self.main_header.fx_list + 2
        self.fx_data = []
        for i in range(self.fx_cnt):
            dat_start, vtx_cnt = self.unpack_type(offset, ">2H")
            offset += 4
            vtx_refs = [self.unpack_type(offset + i * 2, ">H") for i in range(vtx_cnt)]
            offset += vtx_cnt * 2
            self.fx_data.append(self._fx_dat(dat_start, vtx_cnt, vtx_refs))

    def get_geo_layout(self):
        start = self.main_header.geo_offset
        offset = 0
        self.geo_cmds = [] # tree
        end = self.parse_geo(start, self.geo_cmds)
        self.end_padding = self.bin_file[offset + start :]

    def parse_geo(self, offset: int, geo_container: list[GeoLayout]):
        cmd_len = 1
        while cmd_len:
            cmd_type, cmd_len = self.unpack_type(offset, ">2L")
            geo = GeoLayout(offset, self.bin_file)
            geo_container.append(geo)
            if geo.child_geo_offset:
                self.parse_geo(offset + geo.child_geo_offset, geo.child_geos)
            offset += geo.length

    # after parsing the necessary basic data, loop through the geo layouts to find all the DLs then write them out
    def write_geos(self, root: bpy.types.Object, geo_container: list[GeoLayout]):
        for geo in geo_container:
            geo_obj = geo.parse_cmd(root)
            if geo.data.cmd_name == "CMD_LOAD_DL":
                mesh = bpy.data.meshes.new("geo load DL")
                [verts, tris] = self.parse_dl(geo.data.dl_offset)
                if tris:
                    mesh.from_pydata(verts, [], tris)
                    geo_obj.data = mesh
            if geo.child_geos:
                self.write_geos(geo_obj, geo.child_geos)

    def parse_dl(self, start: int):
        start = self.main_header.dl_list + start*8
        self.f3d.parse_stream_DL(start)

    # no purpose in using this but I'll leave it for refernce
    def write(self, fileIO):
        # write global include statements
        self.dataclass_write(
            fileIO, self.main_header.type_name, "md_head", self.main_header
        )
        self.dataclass_write(
            fileIO, self.tex_header.type_name, "tx_head", self.tex_header
        )
        self.dataclass_arr(fileIO, "MetaTex", "meta_tex", self.meta_tex_data)
        self.simple_write(fileIO, "// textures would go here\n")
        self.simple_write(fileIO, "// DLs would go here\n")
        # self.simple_write(fileIO, self.dl_cmds)
        self.dataclass_write(
            fileIO, self.vtx_header.type_name, "vtx_head", self.vtx_header
        )
        self.vertices.write(fileIO)
        # self.dataclass_write(fileIO, self.col_header.type_name, "col_head", self.col_header)
        self.dataclass_arr(fileIO, "GeoCubes", "model_geo_cubes", self.geo_cubes)
        self.dataclass_arr(fileIO, "ColTri", "model_col_tris", self.col_tris)
        self.simple_write(fileIO, f"static u16 FxCnt = {self.fx_cnt};\n")
        self.dataclass_arr(fileIO, "FxDat", "model_fx", self.fx_data)
        self.dataclass_arr(fileIO, "GeoLayouts", "model_geos", self.geo_cmds)


# -------------------------------------------------------------------------------
#   Functions
# -------------------------------------------------------------------------------


def get_models(decomp_path: Path):
    map_models = open(decomp_path / Path("src/core2/mapModel.c"), "r")
    models = get_enum_struct_data_from_file(map_models, {"MapModelDescription": ["{", "}"]})[
        "D_8036ABE0"
    ]
    map_models = []
    for line in models:
        line = line.replace("{", "").replace("}", "").split(",")
        if len(line) < 9:
            continue
        line = [a.strip() for a in line]
        min_bounds = line[3:6]
        max_bounds = line[6:9]
        scale = line[9].replace("f", "")
        map_models.append(
            MapModelDescription(*line[0:3], min_bounds, max_bounds, scale)
        )
    return map_models


# do I really even need this?
def get_enums(decomp_path: Path):
    enums_file = open(decomp_path / Path("include/enums.h"), "r")
    enums = get_enum_struct_data_from_file(enums_file, {"enum": [None, None]})
    return enums


def extract_model(decomp_path: Path, map_model: MapModelDescription):
    # opa model
    opa_model_id = decomp_path / Path("assets/model") / f"{map_model.get_opa_asset_num()}.model.bin"
    with open(opa_model_id, "rb") as bin_file:
        bin_file = bin_file.read()
        # map_model.get_opa_asset_num()
        block = ModelBin(bin_file)
        lvl_root = bpy.data.objects.new("Empty", None)
        lvl_root.name = f"{map_model.get_opa_asset_num()}.model.bin"
        lvl_root.fast64.bk64.obj_type = "Level Root"
        block.write_geos(lvl_root, block.geo_cmds)
    # xlu model
    xlu_model_id = decomp_path / Path("assets/model") / f"{map_model.get_xlu_asset_num()}.model.bin"
    with open(xlu_model_id, "rb") as bin_file:
        bin_file = bin_file.read()
        # map_model.get_xlu_asset_num()
        block = ModelBin(bin_file)


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------


class BK64_LevelImport(Operator):
    bl_label = "Import Level"
    bl_idname = "wm.bk64_import_level"

    def execute(self, context):
        scene = context.scene
        props = scene.fast64.bk64.importer

        col = context.collection
        if props.use_collection:
            obj_col = f"{props.level_name} objs"
        else:
            obj_col = None

        decomp_path = Path(bpy.path.abspath(props.decomp_path))
        model_list = get_models(decomp_path)
        enums = get_enums(decomp_path)
        extract_model(decomp_path, model_list[0])
        return {"FINISHED"}


# ------------------------------------------------------------------------
#    Props
# ------------------------------------------------------------------------


class BK64_ImportProperties(PropertyGroup):
    # level props
    decomp_path: StringProperty(name="Decomp Path", subtype="FILE_PATH", description="Path of decomp repo")
    scale: FloatProperty(name="F3D Blender Scale", default=100)
    level_enum: EnumProperty(name="Level", description="Choose a level", items=[("test", "test", "test")], default="test")
    custom_level_name: StringProperty(
        name="Custom Level Name",
        description="Custom level name",
        default="",
    )
    force_new_tex: BoolProperty(
        name="force_new_tex",
        description="Forcefully load new textures even if duplicate path/name is detected",
        default=False,
    )
    as_obj: BoolProperty(
        name="As OBJ", description="Make new materials as PBSDF so they export to obj format", default=False
    )
    use_collection: BoolProperty(
        name="use_collection", description="Make new collections to organzie content during imports", default=True
    )
    export_friendly: BoolProperty(
        name="Export Friendly",
        description="Format import to be friendly for exporting for hacks rather than importing a 1:1 representation",
        default=True,
    )

    import_target: EnumProperty(
        name="Import Target",
        description="Choose a level",
        items=[("C", "C", "C"), ("Binary", "Binary", "Binary")],
        default="C",
    )

    @property
    def level_name(self):
        if self.level_enum == "Custom":
            return self.custom_level_name
        else:
            return self.level_enum

    def draw_level(self, layout: bpy.types.UILayout):
        # prop_split(layout, self, "import_target", "Import Target")
        layout.prop(self, "decomp_path")
        layout.separator()
        box = layout.box()
        box.label(text="Level Importer")
        box.prop(self, "level_enum")
        if self.level_enum == "Custom":
            box.prop(self, "custom_level_name")
        row = box.row()
        row.prop(self, "force_new_tex")
        row.prop(self, "as_obj")
        row.prop(self, "export_friendly")


class BK64_ObjectProperties(PropertyGroup):
    # just placeholder stuff
    obj_type: StringProperty(name="Obj type")
    geo_type: StringProperty(name="Geo type")
    geo_args: StringProperty(name="geo args")


# ------------------------------------------------------------------------
#    Panels
# ------------------------------------------------------------------------


class BK64_ImportPanel(BK64_Panel):
    bl_label = "BK64 Importer"
    bl_idname = "bk64_PT_importer"
    bl_context = "objectmode"
    import_panel = True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_props = scene.fast64.bk64.importer
        importer_props.draw_level(layout)
        layout.operator("wm.bk64_import_level")


classes = (
    BK64_ImportProperties,
    BK64_ObjectProperties,
    BK64_LevelImport,
)


def bk64_import_panel_register():
    register_class(BK64_ImportPanel)


def bk64_import_register():
    for cls in classes:
        register_class(cls)


def bk64_import_panel_unregister():
    unregister_class(BK64_ImportPanel)


def bk64_import_unregister():
    for cls in reversed(classes):
        unregister_class(cls)
