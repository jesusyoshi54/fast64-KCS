# ------------------------------------------------------------------------
#    Header
# ------------------------------------------------------------------------
from __future__ import annotations

import bpy

import os, struct, math, enum
from functools import lru_cache
from pathlib import Path
from mathutils import Vector, Euler, Matrix
from collections import namedtuple
from dataclasses import dataclass
from copy import deepcopy
from re import findall
from typing import BinaryIO, TextIO, Any

from . import f3dex2
from .kcs_anims import import_anim_bin
from .kcs_utils import *
from .kcs_data import (
    geo_block_includes,
    geo_block_header_struct,
    layout_struct,
    texture_scroll_struct,
)

from ..utility_importer import *
from ..utility import (
    propertyGroupGetEnums,
    checkUniqueBoneNames,
    duplicateHierarchy,
    cleanupDuplicatedObjects,
    transform_mtx_blender_to_n64,
    yUpToZUp,
    getFMeshName,
    parentObject,
    PluginError,
)
from ..f3d.f3d_bleed import BleedGraphics
from ..f3d.f3d_import import Tile, Texture, Mat, DL
from ..f3d.f3d_writer import (
    getInfoDict,
    saveStaticModel,
    TriangleConverterInfo,
)
from ..f3d.f3d_gbi import (
    DLFormat,
    GfxListTag,
    GfxMatWriteMethod,
    GfxFormatter,
    GfxList,
    FModel,
    FMesh,
    FMaterial,
    DPSetTextureImage,
)


# ------------------------------------------------------------------------
#    Classes
# ------------------------------------------------------------------------

# geo data

# import only classes


class Vertices:
    _Vec3 = namedtuple("Vec3", "x y z")
    _UV = namedtuple("UV", "s t")
    _color = namedtuple("rgba", "r g b a")

    def __init__(self):
        self.UVs = []
        self.VCs = []
        self.Pos = []

    def _make(self, v: tuple):
        self.Pos.append(self._Vec3._make(v[0:3]))
        self.UVs.append(self._UV._make(v[4:6]))
        self.VCs.append(self._color._make(v[6:10]))  # holds norms and vcs when importing


# this is the class that holds the actual individual scroll struct and textures
class tx_scroll:
    _scroll = namedtuple("texture_scroll", " ".join([x[1] for x in texture_scroll_struct.values()]))

    def __init__(self, *args: tuple):
        self.scroll = self._scroll._make(*args)


# each texture scroll will start from an array of ptrs, and each ptr will reference
# tex scroll data
class Tex_Scroll(BinProcess, BinWrite):
    def extract_dict(self, start, dict):
        a = []
        for k, v in dict.items():
            try:
                if v[3]:
                    a.append(self.upt(start + k, v[0], v[2]))
            except:
                a.append(self.upt(start + k, v[0], v[2]))
        return a

    def __init__(self, scrollPtrs, file, ptr):
        self.scroll_ptrs = scrollPtrs
        self.scrolls = {}
        self.file = file
        self.ptr = ptr
        for p in scrollPtrs:
            if p != 0x99999999 and p:
                # get struct
                scr = tx_scroll(self.extract_dict(self.seg2phys(p), texture_scroll_struct))
                self.scrolls[p] = scr
                # search for palletes
                if scr.scroll.palettes:
                    start = self.seg2phys(scr.scroll.palettes)
                    self.pal_start = scr.scroll.textures
                    scr.palettes = self.get_BI_pairs(start, stop=(0x9999, 0x9999))
                # search for textures
                if scr.scroll.textures:
                    start = self.seg2phys(scr.scroll.textures)
                    self.tx_start = scr.scroll.textures
                    scr.textures = self.get_BI_pairs(start, stop=(0x9999, 0x9999))


# used to parse imports with specific kirby information, works on entire layouts
class KCS_F3d(DL):
    def __init__(self, last_mat = None):
        self.last_layout = None
        self.cur_geo = None
        super().__init__(lastmat = last_mat)

    # the dl stream is already split into a tuple of name, args so
    # I'll alter the parsing bhv to reflect that
    def parse_stream(self, dat_stream: Sequence[Any], entry_id: Any):
        parser = self.parsed_streams.get(entry_id)
        if not parser:
            self.parsed_streams[entry_id] = (parser := Parser(dat_stream))
        for line in parser.stream():
            cur_macro = Macro(*line)
            func = getattr(self, cur_macro.cmd, None)
            if not func:
                raise Exception(f"Macro {cur_macro} not found in parser function")
            else:
                flow_status = func(cur_macro)
            if flow_status == self.break_parse:
                return

    # use tex scroll struct info to get the equivalent dynamic DL, and set the t_scroll flag to true in mat so when getting mats, I can return an array of mats
    def insert_scroll_dyn_dl(self, Geo, layout, scr_num):
        Tex_Scroll = Geo.tex_scrolls[Geo.tex_header[layout.index]]
        scr = Tex_Scroll.scrolls[Tex_Scroll.scroll_ptrs[scr_num]]
        self.LastMat.tx_scr = scr
        flgs = scr.scroll.flags
        # do textures and palettes by taking only the first texture, the rest will have to go into the scroll object
        if flgs & 3:
            Timg = scr.textures[0]
            Fmt = scr.scroll.fmt1
            Siz = scr.scroll.siz1
            loadtex = Texture(Timg, Fmt, Siz)
            loadtex.scr_tex = scr.textures[:-1]
            self.LastMat.loadtex = loadtex
            # if both textures are present, dyn DL loads tex1 (tile 6)
            # this results in both just being the same as far as my
            # export is concerned, but I will replicate DL bhv
            if flgs & 3 == 3:
                self.LastMat.tex1 = loadtex
                self.LastMat.tex1.scr_tex = scr.textures[:-1]
        # if there is both a tex and a palette, then the load TLUT
        # is inside of the dyn DL, otherwise it isn't
        if flgs & 4:
            Timg = scr.palettes[0]
            Fmt = "G_IM_FMT_RGBA"
            Siz = "G_IM_SIZ_16b"
            pal_tex = Texture(Timg, Fmt, Siz)
            pal_tex.scr_pal = scr.palettes[:-1]
            if scr.scroll.flags & 3:
                self.LastMat.pal = pal_tex
            else:
                self.LastMat.loadtex = pal_tex
        # set some color registers
        if flgs & 0x400:
            self.LastMat.env = scr.scroll.env_col
        if flgs & 0x800:
            self.LastMat.blend = scr.scroll.blend_col
        if flgs & 0x1000:
            self.LastMat.light_col[1] = scr.scroll.light1_col
        if flgs & 0x2000:
            self.LastMat.light_col[2] = scr.scroll.light2_col
        # prim is sort of special and set with various flags
        if flgs & 0x18:
            self.LastMat.prim = (0, scr.scroll.primLODFrac, scr.scroll.prim_col)
        # texture scale
        if flgs & 0x80:
            self.LastMat.tex_scale = (scr.scroll.xScale, scr.scroll.yScale)

    # recursively parse the display list in order to return a bunch of model data
    def get_data_from_dl(self, Geo, layout):
        self.VertBuff = [0] * 32
        self.Tris = []
        self.UVs = []
        self.VCs = []
        self.Verts = []
        self.Mats = []
        self.NewMat = 0
        self.cur_geo = Geo
        self.last_layout = layout
        if hasattr(layout, "DLs"):
            for entry_ptr in layout.entry:
                self.parse_stream(layout.DLs[entry_ptr], entry_ptr)
        return (self.Verts, self.Tris)

    def gsSPBranchList(self, macro: Macro):
        if seg4_ptr := self.eval_dl_segptr(macro.args[0]):
            self.reset_parser(seg4_ptr)
            self.parse_stream(self.last_layout.DLs[seg4_ptr], seg4_ptr)
        else:
            scr_num = (eval(macro.args[0]) & 0xFFFF) // 8
            self.insert_scroll_dyn_dl(self.cur_geo, self.last_layout, scr_num)
            
        return self.break_parse
        
    def gsSPBranchLessZraw(self, macro: Macro):
        if seg4_ptr := self.eval_dl_segptr(macro.args[0]):
            self.reset_parser(seg4_ptr)
            self.parse_stream(self.last_layout.DLs[seg4_ptr], seg4_ptr)
        else:
            scr_num = (eval(macro.args[0]) & 0xFFFF) // 8
            self.insert_scroll_dyn_dl(self.cur_geo, self.last_layout, scr_num)
            
        return self.continue_parse

    def gsSPDisplayList(self, macro: Macro):
        if seg4_ptr := self.eval_dl_segptr(macro.args[0]):
            self.reset_parser(seg4_ptr)
            self.parse_stream(self.last_layout.DLs[seg4_ptr], seg4_ptr)
        else:
            scr_num = (eval(macro.args[0]) & 0xFFFF) // 8
            self.insert_scroll_dyn_dl(self.cur_geo, self.last_layout, scr_num)
        return self.continue_parse
        
    def gsSPVertex(self, macro: Macro):
        args = [int(a) for a in macro.args]
        for i in range(args[2], args[2] + args[1], 1):
            self.VertBuff[i] = len(self.Verts) + i - args[2]
        # verts are pre processed
        self.Verts.extend(self.cur_geo.vertices.Pos[args[0] : args[0] + args[1]])
        self.UVs.extend(self.cur_geo.vertices.UVs[args[0] : args[0] + args[1]])
        self.VCs.extend(self.cur_geo.vertices.VCs[args[0] : args[0] + args[1]])
        return self.continue_parse
        
    def gsDPSetTextureImage(self, macro: Macro):
        self.NewMat = 1
        Timg = (eval(macro.args[3]) >> 16, eval(macro.args[3]) & 0xFFFF)
        Fmt = macro.args[1]
        Siz = macro.args[2]
        loadtex = Texture(Timg, Fmt, Siz)
        self.LastMat.loadtex = loadtex
        return self.continue_parse

    def eval_dl_segptr(self, num):
        num = int(num)
        if num >> 24 == 0xE:
            return None
        else:
            return num

    def apply_f3d_mesh_dat(self, obj: bpy.types.Object, mesh: bpy.types.Mesh, tex_path: Path):
        tris = mesh.polygons
        bpy.context.view_layer.objects.active = obj
        ind = -1
        new = -1
        UVmap = obj.data.uv_layers.new(name="UVMap")
        # I can get the available enums for color attrs with this func
        vcol_enums = propertyGroupGetEnums(bpy.types.FloatColorAttribute, "data_type")
        # enums were changed in a blender version, this should future proof it a little
        if "FLOAT_COLOR" in vcol_enums:
            e = "FLOAT_COLOR"
        else:
            e = "COLOR"
        Vcol = obj.data.color_attributes.get("Col")
        if not Vcol:
            Vcol = obj.data.color_attributes.new(name="Col", type=e, domain="CORNER")
        Valph = obj.data.color_attributes.get("Alpha")
        if not Valph:
            Valph = obj.data.color_attributes.new(name="Alpha", type=e, domain="CORNER")
        self.Mats.append([len(tris), 0])
        for i, t in enumerate(tris):
            if i > self.Mats[ind + 1][0]:
                new = self.create_new_f3d_mat(self.Mats[ind + 1][1], mesh)
                ind += 1
                if not new:
                    new = len(mesh.materials) - 1
                    mat = mesh.materials[new]
                    mat.name = "KCS F3D Mat {} {}".format(obj.name, new)
                    self.Mats[new][1].apply_material_settings(mat, tex_path)
                else:
                    # I tried to re use mat slots but it is much slower, and not as accurate
                    # idk if I was just doing it wrong or the search is that much slower, but this is easier
                    mesh.materials.append(new)
                    new = len(mesh.materials) - 1
            # if somehow ther is no material assigned to the triangle or something is lost
            if new != -1:
                t.material_index = new
                # Get texture size or assume 32, 32 otherwise
                i = mesh.materials[new].f3d_mat.tex0.tex
                if not i:
                    WH = (32, 32)
                else:
                    WH = i.size
                # Set UV data and Vertex Color Data
                for v, l in zip(t.vertices, t.loop_indices):
                    uv = self.UVs[v]
                    vcol = self.VCs[v]
                    # scale verts. I just copy/pasted this from kirby tbh Idk
                    UVmap.data[l].uv = [a * (1 / (32 * b)) if b > 0 else a * 0.001 * 32 for a, b in zip(uv, WH)]
                    # idk why this is necessary. N64 thing or something?
                    UVmap.data[l].uv[1] = UVmap.data[l].uv[1] * -1 + 1
                    Vcol.data[l].color = [a / 255 for a in vcol]

    def create_new_f3d_mat(self, mat: SM64_Material, mesh: bpy.types.Mesh):
        # check if this mat was used already in another mesh (or this mat if DL is garbage or something)
        # even looping n^2 is probably faster than duping 3 mats with blender speed
        for j, F3Dmat in enumerate(bpy.data.materials):
            if F3Dmat.is_f3d:
                dupe = mat.mat_hash_f3d(F3Dmat.f3d_mat)
                if dupe:
                    return F3Dmat
        if mesh.materials:
            mat = mesh.materials[-1]
            new = mat.id_data.copy()  # make a copy of the data block
            # add a mat slot and add mat to it
            mesh.materials.append(new)
        else:
            bpy.ops.object.create_f3d_mat()  # the newest mat should be in slot[-1] for the mesh materials
        return None


@dataclass
class Layout(BinProcess, BinWrite):
    flag: int = 0
    depth: int = 0
    ptr: int = 0
    translation: Vector = (0, 0, 0)
    rotation: Vector = (0, 0, 0)
    scale: Vector = (0, 0, 0)
    index: int = 0
    # a manual DL stop
    stop = None

    def __post_init__(self):
        self.symbol_init()

    def __hash__(self):
        return id(self)

    @property
    def is_vfx(self):
        return (self.ptr >> 24) == 0x80

    @property
    def dat(self):
        return [
            self.flag,
            self.depth,
            self.ptr,
            self.translation,
            self.rotation,
            self.scale,
        ]

    def to_c(self):
        CData = KCS_Cdata()
        self.write_dict_struct(self, layout_struct, CData, "Layout", f"Geo_LY_{self.index}")
        return CData


# fake storage class that mirrors methods of layout
@dataclass
class FauxLayout:
    ptr: int
    index: int = 0
    # a manual DL stop
    stop = None

    def __hash__(self):
        return id(self)

    def to_c(self):
        return KCS_Cdata()


# takes binary input and makes geo block data
class GeoBinary(BinProcess):
    _Vec3 = namedtuple("Vec3", "x y z")
    _texture = namedtuple("texture", "fmt siz bank_index")

    def __init__(self, file, scale):
        self.file = file
        self.main_header = self.upt(0, ">8L", 32)
        self.scale = scale
    
    def decode_geo_block(self):
        self.get_tex_scrolls()
        self.DLs = (
            dict()
        )  # this is also in layouts, but I want it raw here to print in RAM order, and in layouts to analyze in the processed order
        self.render_mode = self.main_header[2]
        self._render_mode_map[self.render_mode](self)
        # get vtx and img refs null terminated arrays
        self.get_refs()
        self.get_anims()

    def get_tex_scrolls(self):
        if self.main_header[1]:
            start = self.main_header[1]
            # get header of POINTERS
            self.tex_header = self.get_referece_list(start, stop=0x99999999)
            self.tex_scrolls = {}
            for p in self.tex_header:
                if p and p != 0x99999999:
                    self.tex_scrolls[p] = Tex_Scroll(self.get_referece_list(p, stop=0x99999999), self.file, p)
            # sort scrolls
            self.tex_scrolls = self.sort_dict(self.tex_scrolls)

    # anims are bank indices
    def get_anims(self):
        num = self.main_header[5]
        start = self.seg2phys(self.main_header[6])
        self.anims = self.get_BI_pairs(start, num=num)

    # both types of refs are null terminated lists
    def get_refs(self):
        self.img_refs = self.get_referece_list(self.main_header[3])
        self.vtx_refs = self.get_referece_list(self.main_header[4])

    # no layout, just a single DL
    def decode_layout_13(self):
        L = FauxLayout(self.seg2phys(self.main_header[0]))
        L.eval_dl_segptrs = [L.ptr]
        self.layouts = [L]
        self.decode_f3d_bin(L)
        Vert_End = L.ptr[0]
        self.decode_vertices(32, Vert_End)

    # no layouts, just an entry point
    def decode_layout_14(self):
        L = FauxLayout(self.seg2phys(self.main_header[0]))
        self.decode_entry(L)
        self.layouts = [L]
        self.decode_f3d_bin(L)
        Vert_End = L.ptr[0]
        self.decode_vertices(32, Vert_End)

    # layouts point to DL
    def decode_layout_17(self):
        self.get_layouts()
        starts = []
        for l in self.layouts:
            if l.ptr and (l.ptr >> 24) == 0x04:
                l.eval_dl_segptrs = [l.ptr]
                starts.extend(self.decode_f3d_bin(l))
        if starts:
            Vert_End = min(starts)
            self.decode_vertices(32, Vert_End)

    # layouts point to entry point
    def decode_layout_18(self):
        self.get_layouts()
        starts = []
        for l in self.layouts:
            if l.ptr and (l.ptr >> 24) == 0x04:
                self.decode_entry(l)
                starts.extend(self.decode_f3d_bin(l))
        if starts:
            Vert_End = min(starts)
            self.decode_vertices(32, Vert_End)

    # layout points to pair of DLs
    def decode_layout_1B(self):
        self.get_layouts()
        starts = []
        for l in self.layouts:
            if l.ptr and (l.ptr >> 24) == 0x04:
                self.decode_dl_pair(l)
                starts.extend(self.decode_f3d_bin(l))
        if starts:
            Vert_End = min(starts)
            self.decode_vertices(32, Vert_End)

    # layout points to entry point with pair of DL
    def decode_layout_1C(self):
        self.get_layouts()
        starts = []
        for l in self.layouts:
            if l.ptr and (l.ptr >> 24) == 0x04:
                self.decode_entry_dbl(l)
                starts.extend(self.decode_f3d_bin(l))
        if starts:
            Vert_End = min(starts)
            self.decode_vertices(32, Vert_End)

    def decode_layout(self, start, index=None):
        start = self.seg2phys(start)
        LY = self.upt(start, ">2HL9f", 0x2C)
        v = self._Vec3._make
        return Layout(*LY[0:3], v(LY[3:6]), v(LY[6:9]), v(LY[9:12]), index=index)

    def get_layouts(self):
        self.layouts = [
            self.decode_layout(self.main_header[0] + 0x2C * i, index=i) for i in range(self.main_header[-1] + 1)
        ]
        # env vfx exists
        if self.layouts[-1].is_vfx:
            start = len(self.layouts)
            x = 0
            while True:
                new_ly = self.decode_layout(self.main_header[0] + 0x2C * (start + x), index=(start + x))
                self.layouts.append(new_ly)
                x += 1
                if new_ly.flag & 0x8000:
                    break

    # has to be after func declarations
    _render_mode_map = {
        0x13: decode_layout_13,
        0x14: decode_layout_14,
        0x17: decode_layout_17,
        0x18: decode_layout_18,
        0x1B: decode_layout_1B,
        0x1C: decode_layout_1C,
    }

    def decode_dl_pair(self, ly: Layout):
        ly.eval_dl_segptrs = []  # just a literal list of ptrs
        ptrs = self.upt(self.seg2phys(ly.ptr), ">2L", 8)
        for ptr in ptrs:
            if ptr:
                ly.eval_dl_segptrs.append(ptr)
        ly.DL_Pair = ptrs

    def decode_entry_dbl(self, ly: Layout):
        x = 0
        start = self.seg2phys(ly.ptr)
        ly.entry_dbls = []
        ly.eval_dl_segptrs = []  # just a literal list of ptrs
        while True:
            mark, *ptrs = self.upt(start + x, ">3L", 12)
            ly.entry_dbls.append((mark, ptrs))
            if mark == 4:
                return
            else:
                for ptr in ptrs:
                    if ptr:
                        ly.eval_dl_segptrs.append(ptr)
            x += 12
            # shouldn't execute
            if x > 120:
                print("your while loop is broken in GeoBinary.decode_entry")
                break

    def decode_entry(self, ly: Layout):
        x = 0
        start = self.seg2phys(ly.ptr)
        ly.entry_pts = []  # the actual entry pt raw data
        ly.eval_dl_segptrs = []  # just a literal list of ptrs
        while True:
            mark, ptr = self.upt(start + x, ">2L", 8)
            ly.entry_pts.append((mark, ptr))
            if mark == 4:
                return
            if ptr == 0:
                continue
            else:
                ly.eval_dl_segptrs.append(ptr)
            x += 8
            # shouldn't execute
            if x > 80:
                print("your while loop is broken in GeoBinary.decode_entry")
                break

    # gonna use a module for this
    def decode_f3d_bin(self, ly: Layout):
        DLs = {}
        self.vertices = []
        starts = []
        ly.entry = ly.eval_dl_segptrs[
            :
        ]  # create shallow copy, use this for analyzing DL, while DL ptrs will be a dict including jumped to DLs
        for dl in ly.eval_dl_segptrs:
            start = self.seg2phys(dl)
            starts.append(start)
            f3d = self.decode_dl_bin(start, ly)
            self.DLs[dl] = f3d
            DLs[dl] = f3d
        ly.DLs = DLs
        return starts

    def eval_dl_segptr(self, num):
        if num >> 24 == 0xE:
            return None
        else:
            return num

    def decode_dl_bin(self, start, ly: Layout):
        DL = []
        x = 0
        while True:
            cmd = self.get_f3d_cmd(self.file[start + x : start + x + 8])
            x += 8
            if not cmd:
                continue
            name, args = self.split_args(cmd)
            # check for multi length cmd (branchZ and tex rect generally)
            extra = f3dex2.check_double_cmd(name)
            if extra:
                name, args = f3dex2.fix_multi_cmd(self.file[start + x : start + x + extra], name, args)
                x += extra
            # adjust vertex pointer so it is an index into vert arr
            if name == "gsSPVertex":
                args[0] = str(self.seg2phys(int(args[0]) - 0x20) // 0x10)
            # check for flow control
            if name == "gsSPEndDisplayList":
                break
            elif name == "gsSPDisplayList":
                ptr = self.eval_dl_segptr(int(args[0]))
                if ptr:
                    ly.eval_dl_segptrs.append(ptr)
                DL.append((name, args))
                continue
            elif name == "gsSPBranchLessZraw":
                ptr = self.eval_dl_segptr(int(args[0]))
                if ptr:
                    ly.eval_dl_segptrs.append(ptr)
                DL.append((name, args))
                continue
            elif name == "gsSPBranchList":
                ptr = self.eval_dl_segptr(int(args[0]))
                if ptr:
                    ly.eval_dl_segptrs.append(ptr)
                DL.append((name, args))
                break
            # check for manual stop
            if ly.stop and start + x + 8 > ly.stop:
                break
            DL.append((name, args))
        DL.append((name, args))
        return DL

    @lru_cache(maxsize=32)  # will save lots of time with repeats of tri calls
    def get_f3d_cmd(self, bin):
        return f3dex2.Ex2String(bin)

    def split_args(self, cmd):
        filt = "\(.*\)"
        a = re.search(filt, cmd)
        return cmd[: a.span()[0]], cmd[a.span()[0] + 1 : a.span()[1] - 1].split(",")

    def decode_vertices(self, start, end):
        self.vertices = Vertices()
        for i in range(start, end, 16):
            v = self.upt(i, ">6h4B", 16)
            self.vertices._make(v)


# interim between bpy props and geo blocks, used for importing and exporting
class BpyGeo:
    def __init__(self, rt, scale):
        self.rt = rt
        self.scale = scale

    def enter_edit_mode(self, obj: bpy.types.Object):
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
    
    def apply_mesh_dat_to_obj(self, model_data: KCS_F3d, obj: bpy.types.Object, mesh: bpy.types.Mesh, tex_path: Path, cleanup: bool = True):
        model_data.apply_f3d_mesh_dat(obj, mesh, tex_path)
        # cleanup
        mesh.validate()
        mesh.update(calc_edges=True)
        if cleanup:
            # shade smooth
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode="OBJECT")
            
    def update_transform_stack(self, layout: Layout, transform_stack: list[bpy.types.Object, Matrix], stack_index: int, stack_item: Any):
        # set the transform
        cur_transform = Matrix.LocRotScale(layout.translation, Euler(layout.rotation), layout.scale)
        
        depth = (layout.depth&0xFF)
        
        # adjust stack
        if depth >= stack_index:
            transform_stack.append([])
            stack_index = depth + 1
        else:
            transform_stack = transform_stack[:depth + 2]
            stack_index = depth + 1
        # change the top of the stack to be the parent @ layout transform
        cur_transform = transform_stack[stack_index - 1][1] @ cur_transform
        transform_stack[stack_index] = [stack_item, cur_transform]
        return transform_stack, stack_index
    
    def add_bone_with_transform(self, cur_transform: Matrix, name: str, parent_bone: str):
        self.enter_edit_mode(self.rt)
        edit_bone = self.rt.data.edit_bones.new(name)
        # give it a non zero length
        location = cur_transform.to_translation() * (1/self.scale)
        edit_bone.head = location
        edit_bone.tail = location + Vector((0, 0, 0.1))
        # this is just visual to make the bones the same size, bones aren't actually bendy
        edit_bone.bbone_x = 0.02
        edit_bone.bbone_z = 0.02
        if parent_bone:
            parent = self.rt.data.edit_bones.get(parent_bone)
            parent.tail = edit_bone.head
            edit_bone.parent = parent
            edit_bone.use_connect = True
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        self.rt.pose.bones[name].rotation_mode = "XYZ"
    
    def write_bpy_armature_from_geo(self, name: str, cls: GeoBinary, tex_path: Path, collection: bpy.types.Collection):
        # for now, do basic import, each layout is an object
        transform_stack: list[str, Matrix] = [["", yUpToZUp]]
        stack_index = 0 # everything will go on root
        last_mat = None
        # create dict of models so I can reuse model dat as needed (usually for blocks)
        parsed_models = dict()
        mesh_objs = []
        for i, layout in enumerate(cls.layouts):
            if (layout.depth & 0xFF) == 0x12:
                break
            layout_name = f"{name} {layout.depth&0xFF} {i}"
            # mesh object
            if layout.ptr:
                prev = parsed_models.get(layout.ptr)
                # model was already imported, reuse data block with new obj
                if prev:
                    mesh, last_mat = prev
                else:
                    model_data = KCS_F3d(last_mat=last_mat)
                    (layout.vertices, layout.Triangles) = model_data.get_data_from_dl(cls, layout)
                    last_mat = model_data.LastMat
                    mesh = bpy.data.meshes.new(layout_name)
                    mesh.from_pydata(layout.vertices, [], layout.Triangles)
                    # add model to dict
                    parsed_models[layout.ptr] = (mesh, last_mat)
                obj = bpy.data.objects.new(layout_name, mesh)
                collection.objects.link(obj)
                # set KCS props of obj
                obj.KCS_mesh.mesh_type = "Graphics"
                self.apply_mesh_dat_to_obj(model_data, obj, mesh, tex_path, cleanup = bpy.context.scene.KCS_scene.clean_up)
            else:
                obj = None
            
            transform_stack, stack_index = self.update_transform_stack(layout, transform_stack, stack_index, layout_name)
            cur_transform = transform_stack[stack_index][1]
            
            # make the bone
            self.add_bone_with_transform(cur_transform, layout_name, transform_stack[stack_index - 1][0])
            
            if obj:
                obj.matrix_world = cur_transform * (1/self.scale)
                mesh_objs.append(obj)
                vertex_group = obj.vertex_groups.new(name=layout_name)
                vertex_group.add([vert.index for vert in obj.data.vertices], 1, "ADD")
        
        # merge and deform objects
        override = {**bpy.context.copy(), "selected_editable_objects": mesh_objs, "active_object": mesh_objs[0]}
        with bpy.context.temp_override(**override):
            bpy.ops.object.join()
        parentObject(self.rt, mesh_objs[0], keep=1)
        # armature deform
        mod = mesh_objs[0].modifiers.new("deform", "ARMATURE")
        mod.object = self.rt
    
    def write_bpy_gfx_from_geo(self, name: str, cls: GeoBinary, tex_path: Path, collection: bpy.types.Collection):
        # for now, do basic import, each layout is an object
        transform_stack: list[bpy.types.Object, Matrix] = [[self.rt, yUpToZUp]]
        stack_index = 0 # everything will go on root
        last_mat = None
        # create dict of models so I can reuse model dat as needed (usually for blocks)
        parsed_models = dict()
        for i, layout in enumerate(cls.layouts):
            if (layout.depth & 0xFF) == 0x12:
                break
            # mesh object
            if layout.ptr:
                prev = parsed_models.get(layout.ptr)
                # model was already imported, reuse data block with new obj
                if prev:
                    mesh, last_mat = prev
                else:
                    model_data = KCS_F3d(last_mat=last_mat)
                    (layout.vertices, layout.Triangles) = model_data.get_data_from_dl(cls, layout)
                    last_mat = model_data.LastMat
                    mesh = bpy.data.meshes.new(f"{name} {layout.depth&0xFF} {i}")
                    mesh.from_pydata(layout.vertices, [], layout.Triangles)
                    # add model to dict
                    parsed_models[layout.ptr] = (mesh, last_mat)
                obj = bpy.data.objects.new(f"{name} {layout.depth&0xFF} {i}", mesh)
                collection.objects.link(obj)
                # set KCS props of obj
                obj.KCS_mesh.mesh_type = "Graphics"
                self.apply_mesh_dat_to_obj(model_data, obj, mesh, tex_path, cleanup = bpy.context.scene.KCS_scene.clean_up)
            # empty transform
            else:
                obj = make_empty(f"{name} {layout.depth} {i}", "PLAIN_AXES", collection)
                # set KCS props of obj
                obj.KCS_mesh.mesh_type = "Graphics"
            
            transform_stack, stack_index  = self.update_transform_stack(layout, transform_stack, stack_index, obj)
            cur_transform = transform_stack[stack_index][1]
            
            parentObject(transform_stack[stack_index - 1][0], obj, keep=1)
            obj.matrix_world = cur_transform * (1/self.scale)

    # create the fModel cls and populate it with layouts based on child objects
    def init_fModel_from_bpy(self):
        fModel = KCS_fModel(self.rt, bpy.context.scene.saveTextures)
        depth = 0
        fModel.layouts = []
        # create duplicate objects to work on
        fModel.tempObj, fModel.allObjs = duplicateHierarchy(self.rt, None, True, 0)
        # make root location 0 so that area is centered on root
        root_transform = transform_mtx_blender_to_n64()

        # get all child layouts first
        def loop_children(obj, fModel, depth, transform):
            for child in obj.children:
                if self.is_kcs_gfx(child):
                    # each layout contains fMesh data, which holds triangle, and material info
                    fModel.layouts.append(self.create_layout(child, depth, fModel, transform @ child.matrix_local))
                    if child.children:
                        loop_children(child, fModel, depth + 1, transform @ child.matrix_local)

        loop_children(fModel.tempObj, fModel, 1, root_transform)

        # add the root as a layout, though if there are no children, set the render mode to 14
        if not fModel.layouts:
            fModel.render_mode = 0x14  # list of DLs (entry point)
            fModel.layouts.append(FauxLayout(self.export_f3d_from_obj(fModel.tempObj, fModel, Matrix.Identity(4))))
        else:
            fModel.render_mode = 0x18  # list of layouts pointing to entry points
            fModel.layouts.insert(0, self.create_layout(fModel.tempObj, 0, fModel, Matrix.Identity(4)))
            # create final layout
            fModel.layouts.append(Layout(depth=0x12))
        return fModel

    def cleanup_fModel(self, fModel: KCS_fModel):
        cleanupDuplicatedObjects(fModel.allObjs)
        self.rt.select_set(True)
        bpy.context.view_layer.objects.active = fModel.rt

    # create a layout for an obj given its depth and the obj props
    def create_layout(self, obj: bpy.types.Object, depth: int, fModel: KCS_fModel, transform: Matrix):
        # transform layout values to match N64 specs
        # only location needs to be transformed here, because rotation in the mesh data
        # will change the scale and rot
        loc = tuple(transform.translation * self.scale)
        rot = tuple(transform.to_euler("XYZ"))
        scale = tuple(transform.to_scale())
        finalTransform = Matrix.Diagonal(
            Vector((self.scale, self.scale, self.scale))
        ).to_4x4()  # just use the blender scale, other obj transforms can be
        ly = Layout(
            0,
            depth,
            self.export_f3d_from_obj(obj, fModel, finalTransform),
            loc,
            rot,
            scale,
        )
        if obj:
            ly.name = obj.name  # for debug
        return ly

    # creates a list of KCS_fMesh objects with their bpy data processed and stored
    def export_f3d_from_obj(self, tempObj: bpy.types.Object, fModel: KCS_fModel, transformMatrix: Matrix):
        if tempObj and tempObj.type == "MESH":
            try:
                infoDict = getInfoDict(tempObj)
                triConverterInfo = TriangleConverterInfo(tempObj, None, fModel.f3d, transformMatrix, infoDict)
                fMeshes = saveStaticModel(
                    triConverterInfo,
                    fModel,
                    tempObj,
                    transformMatrix,
                    fModel.name,
                    not fModel.write_tex_to_png,
                    False,
                    None,
                )
            except Exception as e:
                self.cleanup_fModel(fModel)
                raise PluginError(str(e))
            return list(fMeshes.values())
        else:
            return 0

    # given an obj, eval if it is a kcs gfx export
    def is_kcs_gfx(self, obj: bpy.types.Object):
        if obj.type == "MESH":
            return obj.KCS_mesh.mesh_type == "Graphics"
        if obj.type == "EMPTY":
            return obj.KCS_obj.KCS_obj_type == "Graphics"


# export only classes


class EntryEnums(enum.Enum):
    Start = 0
    Continue = 1
    End = 4

    def __str__(self):
        return f"{self.value}"


# holds a list of DL ptrs
class EntryPoint(BinWrite):
    def __init__(self, fMeshes: list[FMesh], index: int = 0):
        self.fMeshes = fMeshes
        self.targets = []
        self.symbol_init()
        self.index = index
        for fMesh in fMeshes:
            if fMesh.draw:
                # first member is enumerated 0, others are enumerated 1
                self.targets.append(
                    [
                        EntryEnums.Continue if self.targets else EntryEnums.Start,
                        self.add_target(fMesh.draw, cast="Gfx *"),
                    ]
                )
        if self.targets:
            self.targets.append([EntryEnums.End, "NULL"])

    def to_c(self):
        CData = KCS_Cdata()
        self.write_arr(CData, "struct EntryPoint", f"EntryPoint_{self.index}", self.targets, self.format_arr, outer_only=True, length=len(self.targets))
        # add pointers
        self.ptr_obj(self, CData, f"&EntryPoint_{self.index}")
        return CData


# subclassed to manage pointers when writing
class KCS_GFXList(GfxList, BinWrite):
    def __init__(self, name, tag, DLFormat):
        super().__init__(name, tag, DLFormat)
        self.symbol_init()

    def to_c_static(self):
        # set symbol if obj is a ptr target
        self.ptr_obj(self, None, f"{self.name}")
        data = f"Gfx {self.name}[] = {{\n"
        for j, command in enumerate(self.commands):
            self.ptr_obj(command, None, f"&{self.name}[{j}]", multi=self)
            data += f"\t{command.to_c(True)},\n"
        data += "};\n\n"
        return data


# a data class that will hold various primitive geo classes and then write them out to files
# population of the classes will be done by BpyGeo or GeoBinary
class KCS_fModel(FModel, BinWrite):
    def __init__(self, rt: bpy.types.Object, write_tex_to_png: bool, name="Kirby"):
        super().__init__("F3DEX2/LX2", False, name, DLFormat.Static, GfxMatWriteMethod.WriteAll)
        self.rt = rt
        self.gfxFormatter = GfxFormatter(None, 2, None)
        self.ptrManager = PointerManager()
        self.img_refs = []
        self.write_tex_to_png = write_tex_to_png

    def getRenderMode(self, draw_layer):
        return ("G_RM_AA_ZB_OPA_SURF", "G_RM_AA_ZB_OPA_SURF2")

    # overrides of base class
    def addMesh(self, name, namePrefix, drawLayer, isSkinned, contextObj):
        meshName = getFMeshName(name, namePrefix, drawLayer, isSkinned)
        checkUniqueBoneNames(self, meshName, name)
        self.meshes[meshName] = KCS_fMesh(meshName, self.DLFormat)
        self.onAddMesh(self.meshes[meshName], contextObj)
        return self.meshes[meshName]

    def addMaterial(self, materialName: str):
        return KCS_fMaterial(materialName, self.DLFormat)

    # KCS specific methods
    # process the layouts after the KCS_fMesh objects have been added, with their tri and mat info
    def process_layouts(self):
        self.symbol_init()
        self.main_header = StructContainer(
            (
                self.add_target(self.layouts[0], cast="struct Layout *"),  # *layout[]
                0,  # *tex_scroll[]
                self.render_mode,
                self.pointer_truty(self.img_refs, cast="Gfx **"),  # *img_refs[]
                0,  # *vtx_refs[]
                0,  # Num_Anims
                0,  # *Anims[]
                len(self.layouts) - 1,  # num layouts
            )
        )
        for j, ly in enumerate(self.layouts):
            ly.index = j
            if not ly.ptr:
                continue
            ly.entry = EntryPoint(ly.ptr, j)
            ly.ptr = ly.add_target(ly.entry, cast="struct EntryPoint *")

        # bleed data
        bleed_gfx = BleedGraphics()
        bleed_gfx.bleed_fModel(self, self.meshes)

    def layout_data_to_c(self):
        gfx_data = KCS_Cdata()
        vtx_data = KCS_Cdata()
        layout_data = KCS_Cdata()
        raw_data = KCS_Cdata()
        entry_data = KCS_Cdata()
        for ly in self.layouts:
            if ly.ptr:
                entryPoint = ly.entry
                for fMesh in entryPoint.fMeshes:
                    fMesh_gfx_data, fMesh_vtx_data = fMesh.to_c(self.f3d, self.gfxFormatter)
                    gfx_data.append(fMesh_gfx_data)
                    vtx_data.append(fMesh_vtx_data)
                    self.img_refs.extend(fMesh.img_refs)
                entry_data.append(entryPoint.to_c())
            layout_data.append(ly.to_c())
        return (vtx_data, gfx_data, raw_data, entry_data, layout_data)

    # this will try to export in a similar manner as the original format because it looks
    # better, it has no functional use except that the GeoBlockHeader is at the start
    def to_c(self):
        header_data = KCS_Cdata()
        header_data.source += geo_block_includes
        self.write_dict_struct(self.main_header, geo_block_header_struct, header_data, "GeoBlockHeader", "Header")
        c_data_containers = self.layout_data_to_c()
        # add raw graphics data (images, lights etc.), item 2 for ordering
        raw_data = c_data_containers[2]
        # img refs
        if self.write_tex_to_png:
            self.write_arr(raw_data, "Gfx", "img_refs", self.img_refs, self.format_arr)
        # add images
        raw_data.append(
            self.to_c_textures(
                0,
                self.write_tex_to_png,
                "",  # texDir, no way for this to work currently, will need custom fImage class
                8,  # bitSize
            )
        )
        # add lights
        raw_data.append(self.to_c_lights())
        # combine containers into one
        header_data.extend(c_data_containers)
        # replace plcaeholder pointers in file with real symbols
        self.resolve_ptrs_c(header_data)
        return header_data


# subclassed to manage pointers when writing, and for dynamic DLs with scrolls
class KCS_fMesh(FMesh, BinWrite):
    def __init__(self, name, dlFormat: DLFormat):
        self.name = name
        # GfxList
        self.draw = KCS_GFXList(name, GfxListTag.Draw, dlFormat)
        # list of FTriGroup
        self.triangleGroups: list["FTriGroup"] = []
        # VtxList
        self.cullVertexList = None
        # dict of (override Material, specified Material to override,
        # overrideType, draw layer) : GfxList
        self.drawMatOverrides = {}
        self.DLFormat = dlFormat

        # Used to avoid consecutive calls to the same material if unnecessary
        self.currentFMaterial = None

        # Props used for KCS specifically
        self.img_refs = []
        self.symbol_init()

    # after each triGroup is added to fMesh.draw, add the DPSetTextureImage as pointer targets, and add the pointer objects to img refs
    def onTriGroupBleedEnd(self, f3d: F3D, triGroup: FTriGroup, last_mat: FMaterial, bleed: BleedGfx):
        for tile, texGfx in enumerate(bleed.bled_tex):
            set_tex = (c for c in texGfx.commands if type(c) == DPSetTextureImage)
            for set_img in set_tex:
                self.img_refs.append(self.add_target(set_img, multi=self.draw))


# subclassed to manage pointers when writing, and for dynamic DLs with scrolls
class KCS_fMaterial(FMaterial):
    def __init__(self, name: str, dlFormat: DLFormat):
        super().__init__(name, dlFormat)
        self.name = name


# ------------------------------------------------------------------------
#    Exorter Functions
# ------------------------------------------------------------------------


def export_geo_c(name: str, obj: bpy.types.Object, context: bpy.types.Context):
    scale = context.scene.KCS_scene.scale
    blend_geo = BpyGeo(obj, scale)
    # create writer class using blender data, with layouts that have fMesh data
    fModel = blend_geo.init_fModel_from_bpy()
    blend_geo.cleanup_fModel(fModel)  # processing of bpy data is done
    fModel.process_layouts()
    cData = fModel.to_c()
    with open(f"{name}.c", "w") as file:
        file.write(cData.source)
    with open(f"{name}.h", "w") as file:
        file.write(cData.header)


# ------------------------------------------------------------------------
#    Importer
# ------------------------------------------------------------------------

def import_geo_bin_anims(bin_file: Path, context: bpy.types.Context, base_path: Path, name: str):
    with open(bin_file, "rb") as geo_bin:
        geo_block = GeoBinary(geo_bin.read(), context.scene.KCS_scene.scale)
        geo_block.get_anims()
    max_frame = 0
    for anim in geo_block.anims:
        anim_path = base_path / "anim" / f"bank_{anim[0]}" / f"{anim[1]}" / "anim.bin"
        last_frame = import_anim_bin(context, anim_path, f"KCS gfx: {name} anim: {anim[1]}")
        if last_frame > max_frame:
            max_frame = last_frame
    # set the scene end frames
    context.scene.frame_end = max_frame

@time_func
def import_geo_bin(bin_file: Path, context: bpy.types.Context, name: str, path: Path):
    # decode geo block
    with open(bin_file, "rb") as geo_bin:
        geo_block = GeoBinary(geo_bin.read(), context.scene.KCS_scene.scale)
        geo_block.decode_geo_block()
    
    # setup the root object and root collection
    if context.scene.KCS_scene.use_collections:
        gfx_collection = bpy.data.collections.new(name)
        context.scene.collection.children.link(gfx_collection)
    else:
        gfx_collection = context.scene.collection
    if context.scene.KCS_scene.import_armature:
        root = bpy.data.objects.new(name, bpy.data.armatures.new(name))
        gfx_collection.objects.link(root)
        root.data.display_type = "BBONE"
    else:
        root = make_empty(name, "PLAIN_AXES", gfx_collection)
        root.KCS_obj.KCS_obj_type = "Graphics"
    
    # write the data out to blender
    write = BpyGeo(root, context.scene.KCS_scene.scale)
    if context.scene.KCS_scene.import_armature:
        write.write_bpy_armature_from_geo("geo", geo_block, path, gfx_collection)
    else:
        write.write_bpy_gfx_from_geo("geo", geo_block, path, gfx_collection)
