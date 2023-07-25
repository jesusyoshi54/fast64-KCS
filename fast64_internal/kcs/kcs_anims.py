# ------------------------------------------------------------------------
#    Header
# ------------------------------------------------------------------------
from __future__ import annotations

import bpy

import os, struct, math, enum
from functools import lru_cache
from pathlib import Path
from mathutils import Vector, Euler, Matrix
from dataclasses import dataclass, field
from copy import copy
from typing import BinaryIO, TextIO, Any

from .kcs_utils import *
from .kcs_data import (
    anim_data_includes,
    anim_header,
    anim_cmd_enums,
)

from ..utility import (
    propertyGroupGetEnums,
    yUpToZUp,
    transform_mtx_blender_to_n64,
    PluginError,
)


# ------------------------------------------------------------------------
#    Classes
# ------------------------------------------------------------------------


# this animation class holds all the anim data in the file
class AnimBin(BinProcess, BinWrite):
    def __init__(self, file: BinaryIO):
        self.file = file
        self.anim_header = self.upt(0, ">3L", 12)
        num_parts = self.anim_header[2]
        self.mode = self.anim_header[1]
        self.anim_scripts = {}
        self.anim_offsets = []
        self.anim_starts = []
        self.virtual_offsets = [self.upt(12 + 4 * i, ">L", 4) for i in range(num_parts)]
        # mode 2 just starts
        if self.mode == 2:
            return self.decode_mode_2(file)
        data_start = min(self.upt(offset, ">L", 4) for offset in self.virtual_offsets)
        head = self.anim_header[0]
        while head < data_start:
            start = self.upt(head, ">L", 4)
            self.anim_offsets.append(start)
            head += 4
        if self.mode == 0:
            return self.decode_mode_0(file)
        elif self.mode == 1:
            return self.decode_mode_1(file)

    def decode_mode_0(self, file):
        for index, bone in enumerate(self.anim_offsets):
            if bone == 0:
                continue
            self.anim_scripts[bone] = AnimScript(file, bone)
            self.anim_starts.append(bone)
        # self.virtual_offsets = [
            # self.get_symbol_from_locations(
                # {
                    # "anim_script_{}{}": self.anim_starts,
                    # "anim_offsets{1}": [self.anim_header[0]],
                # },
                # offset,
                # size=4,
            # )
            # for offset in self.virtual_offsets
        # ]
        # self.anim_offsets = [
            # self.get_symbol_from_locations(
                # {
                    # "anim_offsets{1}": [self.anim_header[0]],
                    # "anim_script_{}{}": self.anim_starts
                # }, offset, size=4
            # )
            # for offset in self.anim_offsets
        # ]
    
    def decode_mode_1(self, file):
        self.texture_scroll_anims = []
        ranges = [offset for offset in self.anim_offsets if offset]
        ranges = [*sorted(ranges), len(file)]
        for start, end in zip(ranges[0::1], ranges[1::1]):
            head = start
            scrolls = []
            while head < end:
                start = self.upt(head, ">L", 4)
                self.texture_scroll_anims.append(start)
                if start:
                    self.anim_scripts[start] = AnimScript(file, start)
                    self.anim_starts.append(start)
                head += 4
        # self.virtual_offsets = [
            # self.get_symbol_from_locations(
                # {
                    # "anim_offsets{1}": [self.anim_header[0]],
                    # "anim_script_{}{}": self.anim_starts,
                    # "scroll_offsets{1}": [
                        # min([off for off in self.anim_offsets if off])
                    # ],
                # },
                # offset,
                # size=4,
            # )
            # for offset in self.virtual_offsets
        # ]
        # self.anim_offsets = [
            # self.get_symbol_from_locations(
                # {"scroll_offsets{1}": [ranges[0]]}, offset, size=4
            # )
            # for offset in self.anim_offsets
        # ]
    
    def decode_mode_2(self, file):
        self.anim_scripts[0] = AnimScript(file, self.anim_header[0])

    def Write(self, file):
        # write comment with file location
        if self.ptrs:
            file.write(
                f"//start 0x{self.ptrs[0]:X} - end 0x{self.ptrs[1]:X}\n{anim_data_includes}\n"
            )
        # write global include statements

        self.WriteDictStruct(
            self.anim_header,
            anim_header,
            file,
            "",
            "Animheader Animation_Header",
            symbols=self.symbols,
            static=True,
        )

        if self.mode != 2:
            self.write_arr(
                file,
                "void *virtual_offsets",
                self.virtual_offsets,
                self.format_arr_ptr,
                length=self.anim_header[2],
                static=True,
                prefix="&"
            )

        if self.mode != 2:
            self.write_arr(
                file,
                "void *anim_offsets",
                self.anim_offsets,
                self.format_arr_ptr,
                length=len(self.anim_offsets),
                static=True,
                prefix="&"
            )

        for anims in self.anim_scripts:
            anims.write(file)
            self.add_header_child(anims)

        if self.mode == 1:
            self.write_arr(
                file,
                "void *scroll_offsets",
                self.texture_scroll_anims,
                self.format_arr_symbols,
                length=len(self.texture_scroll_anims),
                static=True,
                symbols=self.symbols,
            )


class AnimScript(BinProcess, BinWrite):
    debug = False
    def __init__(self, file, start):
        self.file = file
        x = 0
        self.cmds = []
        self.header = []
        self.start = start
        while True:
            cmd = self.upt(start + x, ">L", 4)
            if self.debug:
                print(f"cmd start: 0x{start + x:X}", f"file length: {len(file):X}")
            anim_cmd = self.get_cmd(cmd)
            if self.debug:
                print(anim_cmd)
            x += anim_cmd.unpack_transform(file, start + x)
            self.cmds.append(anim_cmd)
            if anim_cmd.cmd in [0x0, 0xE] or (start + x) >= len(file):
                break

    def unique_cmds(self):
        return set(cmd.cmd for cmd in self.cmds)

    def get_cmd(self, cmd):
        case = cmd >> 25
        if self.debug:
            print(f"cmd MSB: 0x{case:X}")
        assert case < 24
        scale = cmd & 0x7FFF
        transform = ((cmd << 7) >> 0x16) & 0x3FF
        # cmds over 0x10 use integer arguments, they seem to affect some
        # sort of texture scroll channel
        if case in [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]:
            # I won't know which channel is what, at least for now
            num_chans = bin(transform).count("1")
            chan_transform = [ChannelTransform(transform, case, "Field") for i in range(num_chans)]
            anim_cmd = AnimCmd(case, scale, chan_transform, transform_bitfield = transform)
        # aforementioned cmds just have single transform/value
        elif case not in [0x0, 0x1, 0x2, 0xC, 0xD, 0xE]:
            rotate_transform = FieldTransform(transform & 0x7, "rotation_euler", has_vel = (case in [0x5, 0x6]))
            translate_transform = FieldTransform((transform & 0x70) >> 4, "location", has_vel = (case in [0x5, 0x6]))
            scale_transform = FieldTransform((transform & 0x380) >> 7, "scale", has_vel = (case in [0x5, 0x6]))
            base_transform = ChannelTransform(transform & 0x8, case, "Base", has_vel = (case in [0x5, 0x6]))
            transforms = [base_transform, rotate_transform, translate_transform, scale_transform]
            anim_cmd = AnimCmd(case, scale, transforms, transform_bitfield = transform)
        else:
            anim_cmd = AnimCmd(case, scale, None, transform_bitfield = transform)
        return anim_cmd

    def write(self, file):
        length = sum([cmd.length() for cmd in self.cmds])
        self.add_header_data(f"AnimScript anim_script_{self.start:X}[{length}]", static=True)
        file.write(f"static AnimScript anim_script_{self.start:X}[{length}] = {{\n")
        for cmd in self.cmds:
            cmd.write(file)
        file.write("};\n\n")


class ChannelTransform(BinProcess):
    def __init__(self, field, cmd, name: str = "", has_vel: bool = False):
        self.field = field or None
        self.cmd = cmd
        self.name = name
        # a vel cmd has two floats per field
        self.has_vel = has_vel

    def __bool__(self):
        return self.has_transform

    def __str__(self):
        return str(self.field)

    def __format__(self, format_spec):
        return format(self.field, format_spec)

    def length(self):
        if self.has_vel:
            return 8
        else:
            return 4 if self.has_transform else 0

    @property
    def has_transform(self):
        return self.field != None

    def transform_fields(self, scale):
        return []

    def write(self):
        if is_arr(self.field):
            return f"Color{str(self.field)}"
        else:
            return f"{self.name}({self.field})"

    def unpack_dat(self, dat: bytes):
        if self.cmd == 0x11:
            return self.unpack_int(dat)
        if self.cmd > 0x11 and self.cmd < 0x17:
            return self.unpack_scroll(dat)
        else:
            return self.unpack_float(dat)

    def unpack_int(self, dat: bytes):
        self.file = dat
        self.field = self.upt(0, ">L", 4)
        return 4

    def unpack_float(self, dat: bytes):
        self.file = dat
        self.field = self.upt(0, ">f", 4)
        return 4

    def unpack_scroll(self, dat: bytes):
        self.file = dat
        if self.cmd in [0x17]:
            self.field = self.upt(0, ">f", 4)
            return 4
        else:
            self.field = self.upt(0, ">4B", 4)
            return 4

@dataclass
class FieldFrame:
    path: str
    arr_index: int
    value: float
    vel: float
    
    def rest_pos_relative(self, bone_rest_position: Matrix):
        vector_val = Vector()
        vector_val[self.arr_index] = self.value
        if self.path == "location":
            new_val = bone_rest_position.inverted() @ Matrix.LocRotScale(vector_val, None, None)
            self.value = new_val.translation[self.arr_index]
            return
        if self.path == "scale":
            new_val = bone_rest_position.inverted() @ Matrix.LocRotScale(None, None, vector_val) 
            self.value = new_val.to_scale()[self.arr_index]
            return
        if self.path == "rotation_euler":
            self.value = (yUpToZUp @ vector_val)[self.arr_index]
            return


class FieldTransform(BinProcess):
    def __init__(self, bit_field: int, name: str, has_vel: bool = False):
        self.x = bit_field & 4 != 0
        self.y = bit_field & 2 != 0
        self.z = bit_field & 1 != 0
        # separate these so I can transform them separately
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        # a vel cmd has two floats per field
        self.has_vel = has_vel
        self._len = sum(self.fields) * 4 * (1 + has_vel)
        self.name = name

    def __bool__(self):
        return self.has_transform

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}"

    @property
    def has_transform(self):
        return any([self.exists(field) for field in self.fields])

    @property
    def fields(self):
        return self.x, self.y, self.z
      
    @property
    def z_up_fields(self):
        return self.x, self.z, self.y
        
    def vel_z_up_fields(self, scale):
        if self.name == "location":
            return (Vector((self.vel_x, self.vel_z, self.vel_y)) * (1 / scale))
        else:
            return self.vel_x, self.vel_z, self.vel_y
            
    def vel_fields(self, scale):
        if self.name == "location":
            return (Vector((self.vel_x, self.vel_y, self.vel_z)) * (1 / scale))
        else:
            return self.vel_x, self.vel_y, self.vel_z

    def bpy_fields(self, scale: float):
        if self.name == "location":
            return (Vector(self.fields) * (1 / scale))
        elif self.name == "rotation_euler":
            return Vector(self.fields)
        else:
            return self.fields

    def transform_fields(self, scale: float):
        return [FieldFrame(self.name, i, field, vel) for i, (field, use, vel) in enumerate(zip(self.bpy_fields(scale), self.fields, self.vel_fields(scale))) if self.exists(use)]
      
    @property
    def write_fields(self):
        fields = []
        for val in self.fields:
            if hasattr(val, "__iter__"):
                fields.extend(val)
            else:
                fields.append(val)
        return fields

    def exists(self, val):
        return val is not False

    def length(self):
        return self._len

    def write(self):
        def str_out(val):
            return f"{val}f"

        return f"{self.name}_{'X' if self.exists(self.x) else ''}{'Y' if self.exists(self.y) else ''}{'Z' if self.exists(self.z) else ''}({', '.join([str_out(val) for val in self.write_fields if val is not False])})"

    def unpack_dat(self, dat: bytes):
        self.file = dat
        head = 0
        
        def up_float(has_vel, head):
            if has_vel:
                return self.upt(head, ">f", 4), self.upt(head + 4, ">f", 4), head + 8
            else:
                return self.upt(head, ">f", 4), 0, head + 4
        
        if self.exists(self.x):
            self.x, self.vel_x, head = up_float(self.has_vel, head)
        if self.exists(self.y):
            self.y, self.vel_y, head = up_float(self.has_vel, head)
        if self.exists(self.z):
            self.z, self.vel_z, head = up_float(self.has_vel, head)
        return head


@dataclass
class AnimCmd(BinProcess):
    cmd: int
    scale: int
    transforms: Union[float, tuple[FieldTransform]]
    cmd_enum: int = 0
    transform_bitfield: int = 0

    def length(self):
        val = 4
        if self.transforms:
            if is_arr(self.transforms):
                val += sum([cmd.length() for cmd in self.transforms])
            else:
                val += self.transforms.length()
        if self.second_transforms:
            val += sum([cmd.length() for cmd in self.second_transforms])
        return val // 4

    def __str__(self):
        if hasattr(self.transforms, "__iter__"):
            transforms = ", ".join(str(transform) for transform in self.transforms)
        else:
            transforms = self.transforms
        return f"cmd: {hex(self.cmd)}, cmd_enum: {hex(self.cmd_enum)}, scale: {self.scale}, transforms: {transforms}"

    def unpack_transform(self, file, start):
        # these cmds have no args
        if self.cmd in [0x0, 0x1, 0x2, 0xC, 0xF, 0x10]:
            return 4

        # these cmds have a fixed number of args
        if not self.transforms:
            self.file = file
            if self.cmd == 0xD:
                self.transforms = ChannelTransform(self.upt(start + 4, ">2L", 8), self.cmd)
                return 12
            if self.cmd == 0xE:
                self.transforms = ChannelTransform(self.upt(start + 4, ">L", 4), self.cmd)
                return 8
            if self.cmd == 0x17:
                self.transforms = ChannelTransform(self.upt(start + 4, ">2f", 8), self.cmd)
                return 12
            raise Exception(f"cmd {self} has no unpacking instructions")

        x = 4
        for transform in self.transforms:
            if not transform or not transform.has_transform:
                continue
            dat = file[start + x : start + x + transform.length()]
            x += transform.unpack_dat(dat)
        return x

    def transform_str(self):
        if not hasattr(self.transforms, "__iter__"):
            return str(self.transforms)
        return ", ".join([transform.write() for transform in self.all_transforms if transform])

    def write_cmd_16(self, file):
        file.write(f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}(0x{self.transform_bitfield:X}, {self.scale}),\n")
    
    def write_cmd_15(self, file):
        file.write(f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}(0x{self.transform_bitfield:X}, {self.scale}),\n")

    def write_cmd_14(self, file):
        file.write(f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}(0x{self.transforms:X}),\n")
        
    def write_cmd_12(self, file):
        file.write(f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}(0x{self.transform_bitfield:X}, {self.scale}),\n")

    def write_cmd_2(self, file):
        file.write(f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}({self.scale}),\n")
    
    def write_cmd_0(self, file):
        file.write(f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}(),\n")

    def write(self, file):
        write_func = getattr(self, f"write_cmd_{self.cmd}", None)
        if write_func:
            write_func(file)
            return
        else:
            file.write(
                f"\t{anim_cmd_enums.get(self.cmd, self.cmd)}(0x{self.transform_bitfield:X}, {self.scale}, {self.transform_str()}),\n"
            )


# iterim between data and blender
class BpyAnim:
    anim_cmd_blocks = (0x3, 0x5, 0x8, 0xA, 0x12, 0x14)
    anim_cmd_lerps = (0x3, 0x4, 0x5, 0x6, 0x8, 0x9, 0x14, 0x15)
    anim_cmd_special = (0x0, 0x1, 0x2, 0xC, 0xD, 0xE, 0xF, 0x10, 0x11, 0x16, 0x17)
    
    def __init__(self, root: bpy.types.Object, scale: float):
        self.root = root
        self.scale = scale
    
    def add_keyframe(self, fcurve: bpy.types.FCurve, frame: int, value: float, handles: str = "VECTOR"):
        keyframe = fcurve.keyframe_points.insert(frame, value)
        keyframe.handle_left_type = handles
        keyframe.handle_right_type = handles
        return keyframe
    
    # data paths go to loc/rot/scale, index to x/y/z
    def get_or_create_fcurve(self, action: bpy.types.Action, data_path: str, index: int):
        if fcurve := action.fcurves.find(data_path, index=index):
            return fcurve
        else:
            fcurve = action.fcurves.new(data_path, index=index)
            fcurve.color_mode = "AUTO_RGB"
            # fcurve.modifiers = "" # add in cycle mod here if required
            return fcurve

    def convert_hermite_spline(self, cmd: AnimCmd, field_frame: FieldFrame, last_keyframe: bpy.types.Keyframe, cur_frame: int):
        # only cmds 5 and 6 set the vel explicitly
        if cmd.cmd in [0x5, 0x6]:
            prev_vel = last_keyframe.handle_right
            next_vel = Vector((cur_frame + (2/3*cmd.scale), field_frame.value - (field_frame.vel*cmd.scale/3)))
        # cusp cmds set a new right handle for starting keyframe, and set the next vel to 0
        elif cmd.cmd in [0x3, 0x4]:
            if cmd.scale != 0:
                vel = (field_frame.value - last_keyframe.co.y)/cmd.scale
                prev_vel = Vector((cur_frame + (2/3*cmd.scale), last_keyframe.co.y - (vel*cmd.scale/3)))
            else:
                prev_vel = (last_keyframe.handle_right.x, 0)
            next_vel = Vector((cur_frame + (2/3*cmd.scale), field_frame.value))
        # ease cmds inherit the prev vel and make the next one zero
        else:
            prev_vel = last_keyframe.handle_right
            next_vel = Vector((cur_frame + (2/3*cmd.scale), field_frame.value))
        
        last_keyframe.handle_left_type = "FREE"
        last_keyframe.handle_right_type = "FREE"
        last_keyframe.handle_right = prev_vel
        
        return next_vel
        
    def parse_cmd(self, action: bpy.types.Action, pose_bone: bpy.types.Bone, bone_rest_position: Matrix, cmd: AnimCmd, cur_frame: int):
        # check if this cmd is in the normal transform group or the meta group, 0x2 is pause so deal with first
        if cmd.cmd == 0x2:
            cur_frame += cmd.scale
            return cur_frame
            
        if cmd.cmd in self.anim_cmd_special:
            # print(cmd, "not processing anim at this moment")
            return cur_frame
        
        # FieldFrame for all the values the transform sets
        animated_fields = (field for transform in cmd.transforms for field in transform.transform_fields(self.scale))
        
        for field_frame in animated_fields:            
            # adjust vals to rest pos relative
            field_frame.rest_pos_relative(bone_rest_position)
            fcurve = self.get_or_create_fcurve(action, pose_bone.path_from_id(field_frame.path), field_frame.arr_index)
            # for a lerp, set the last keyframe to be linear
            if cmd.cmd in self.anim_cmd_lerps:
                if fcurve.keyframe_points:
                    last_keyframe = fcurve.keyframe_points[-1]
                else:
                    last_keyframe = self.add_keyframe(fcurve, cur_frame, 0, handles = "FREE")
                # set prev interpolation to bezier
                last_keyframe.interpolation = "BEZIER"
                next_keyframe = self.add_keyframe(fcurve, cur_frame + cmd.scale, field_frame.value, handles = "FREE")
                next_keyframe.handle_left = self.convert_hermite_spline(cmd, field_frame, last_keyframe, cur_frame)
            # these would all be set cmds
            else:
                keyframe = self.add_keyframe(fcurve, cur_frame + cmd.scale, field_frame.value)
                keyframe.interpolation = "CONSTANT"
            
        if cmd.cmd in self.anim_cmd_blocks:
            cur_frame += cmd.scale
        
        return cur_frame
    
    def add_anim_to_armature(self, anim_block: AnimBin, name: str):
        # only support this for now
        if (anim_block.mode != 0):
            return 0
        
        # create anim data if there is none
        if not self.root.animation_data:
            anim_data = self.root.animation_data_create()
        else:
            anim_data = self.root.animation_data
        
        # create a new action for this animation
        anim_data.action = bpy.data.actions.new(name)
        
        # edit bones are evil and blender should feel bad
        def get_rest_pos(bone_index):
            self.root.select_set(True)
            bpy.context.view_layer.objects.active = self.root
            bpy.ops.object.mode_set(mode="EDIT", toggle=False)
            bone = self.root.data.edit_bones[bone_index]
            mat = bone.matrix
            while(bone.parent is not None):
                mat = bone.parent.matrix.inverted() @ mat
                bone = bone.parent
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            return (transform_mtx_blender_to_n64() @ mat)
        
        # anim_scripts in order should map to the armature bones
        for bone_index, bone_offset in enumerate(anim_block.anim_offsets):
            
            pose_bone = self.root.pose.bones[bone_index]
            script = anim_block.anim_scripts.get(bone_offset, None)
            if not script:
                continue
            cur_frame = 1
            
            # blender anims are rest pos relative, so the transform must account for that
            # keep in mind that pose bones are Y up!! (why)
            bone_rest_position = get_rest_pos(bone_index)

            print(f"bone start: {bone_index} rest pos {bone_rest_position}")
            
            for cmd in script.cmds:
                cur_frame = self.parse_cmd(anim_data.action, pose_bone, bone_rest_position, cmd, cur_frame)
        return cur_frame
    

# -------------------------------------------------------------------------------
# Importer
# -------------------------------------------------------------------------------


def import_anim_bin(context: bpy.types.Context, anim_path: Path, name: str):
    print(anim_path)
    with open(anim_path, "rb") as anim_binary:
        anim_block = AnimBin(anim_binary.read())
    bpy_anim = BpyAnim(context.active_object, context.scene.KCS_scene.scale)
    return bpy_anim.add_anim_to_armature(anim_block, name)