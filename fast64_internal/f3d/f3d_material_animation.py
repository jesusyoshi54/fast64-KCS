from __future__ import annotations

import bpy, math, os
from dataclasses import dataclass, field

# a WIP suite for adding/removing drivers for various properties within fast64, currently built with support for sm64 tile animations
# and called from f3d_material during custom property callbacks

@dataclass
class DriverAnimation:
    driver: bpy.types.Driver
    expressions: list[str] = field(default_factory=list)
    base_value: int = 0
    
    def apply_expression(self):
        self.expressions.append(str(self.base_value))
        expression = " + ".join(self.expressions)
        self.driver.expression = expression


@dataclass
class DriverManager:
    drivers: dict[bpy.types.Driver, DriverAnimation] = field(default_factory=dict)

    def add_driver(self, driver: bpy.types.Driver):
        if driver not in self.drivers:
            self.drivers[driver] = DriverAnimation(driver)
        return self.drivers[driver]
    
    def apply_expressions(self):
        for driver in self.drivers.values():
            driver.apply_expression()


# adds a driver to the data path on object data "data_object" at path "data_path" and uses an index if data is an array.
# if the path already has a driver, then it will instead return the existing FCurve
def get_or_add_driver(block_object, data_object, prop_path, index: int = -1) -> bpy.types.Driver:
    if block_object.animation_data:
        # create the path for the property we will attach the driver to
        abs_prop_path = data_object.path_from_id(prop_path)
        # get fcurve from bpy data path
        driver = block_object.animation_data.drivers.find(abs_prop_path)
        if driver:
            return driver.driver
    return data_object.driver_add(prop_path, index).driver


def get_tex_field_driver(material: bpy.types.Material, desired_group: str, tile_path: str) -> bpy.types.Driver:
    return get_or_add_driver(
        material.node_tree,
        material.node_tree.nodes[desired_group].inputs[tile_path],
        "default_value"
    )


def remove_driver(block_object, data_object, prop_path, index: int = -1):
    if block_object.animation_data:
        # create the path for the property we will attach the driver to
        abs_prop_path = data_object.path_from_id(prop_path)
        # get driver from bpy data path
        driver = block_object.animation_data.drivers.find(abs_prop_path)
        if driver:
            data_object.driver_remove(prop_path, index)


def remove_all_scroll_drivers(material: bpy.types.Material, desired_group: str, tile_index: int):
    remove_driver(material.node_tree, material.node_tree.nodes[desired_group].inputs[f"{tile_index} S Low"], "default_value")
    remove_driver(material.node_tree, material.node_tree.nodes[desired_group].inputs[f"{tile_index} T Low"], "default_value")
    remove_driver(material.node_tree, material.node_tree.nodes[desired_group].inputs[f"{tile_index} S High"], "default_value")
    remove_driver(material.node_tree, material.node_tree.nodes[desired_group].inputs[f"{tile_index} T High"], "default_value")


# here are some generics for setting/getting commonly used drivers and values


# tile scrolls
def set_tile_scroll_drivers(material: bpy.types.Material, desired_group: str, tile_index: int, driver_manager: DriverManager = None) -> DriverManager:
    if not driver_manager:
        driver_manager = DriverManager()
    texture_prop = getattr(material.f3d_mat, f"tex{tile_index}")
    driver_s_0 = driver_manager.add_driver(get_tex_field_driver(material, desired_group, f"{tile_index} S Low"))
    driver_t_0 = driver_manager.add_driver(get_tex_field_driver(material, desired_group, f"{tile_index} T Low"))
    update_driver_on_interval(driver_s_0, *get_tile_scroll_values(texture_prop, s = True))
    update_driver_on_interval(driver_t_0, *get_tile_scroll_values(texture_prop, t = True))
    return driver_manager


# import conflict if gotten from f3d_material
def trunc_tile(val: float):
    return int(val * 4) / 4


def reset_tile_scroll_drivers(material: bpy.types.Material, desired_group: str, tile_index: int):
    texture_prop = getattr(material.f3d_mat, f"tex{tile_index}")
    material.node_tree.nodes[desired_group].inputs[f"{tile_index} S Low"].default_value = trunc_tile(texture_prop.S.low)
    material.node_tree.nodes[desired_group].inputs[f"{tile_index} T Low"].default_value = trunc_tile(texture_prop.T.low)


def get_tile_scroll_values(tex: TextureProperty, s: bool = False, t: bool = False):
    if not tex.tex or (not s and not t):
        return
    if s:
        return (tex.tile_scroll.s, tex.tile_scroll.interval, tex.S.low)
    else:
        return (tex.tile_scroll.t, tex.tile_scroll.interval, tex.T.low)


# uv scrolls
def set_uv_scroll_drivers(material: bpy.types.Material, desired_group: str, tile_index: int, driver_manager: DriverManager = None) -> DriverManager:
    if not driver_manager:
        driver_manager = DriverManager()
    driver_s_0 = driver_manager.add_driver(get_tex_field_driver(material, desired_group, f"{tile_index} S Low"))
    driver_t_0 = driver_manager.add_driver(get_tex_field_driver(material, desired_group, f"{tile_index} T Low"))
    scroll_prop = getattr(material.f3d_mat, f"UVanim{tile_index}")
    texture_prop = getattr(material.f3d_mat, f"tex{tile_index}")
    if scroll_prop.x.animType == "Linear":
        update_driver_linear(driver_s_0, scroll_prop.x.speed, texture_prop.S.low)
    if scroll_prop.x.animType == "Sine":
        update_driver_sinusoidal(driver_s_0, scroll_prop.x.amplitude, scroll_prop.x.frequency, scroll_prop.x.offset, texture_prop.S.low)
    # if scroll_prop.x.animType == "Noise":
        # update_driver_noise(driver_s_0, scroll_prop.x.noiseAmplitude)
    
    if scroll_prop.y.animType == "Linear":
        update_driver_linear(driver_t_0, scroll_prop.y.speed, texture_prop.T.low)
    if scroll_prop.y.animType == "Sine":
        update_driver_sinusoidal(driver_t_0, scroll_prop.y.amplitude, scroll_prop.y.frequency, scroll_prop.y.offset, texture_prop.T.low)
    # if scroll_prop.y.animType == "Noise":
        # update_driver_noise(driver_s_0, scroll_prop.y.noiseAmplitude)
    return driver_manager

# and here are some generic functions for setting driver expressions

# update with speed on an interval, sm64 tile scrolling
def update_driver_on_interval(driver_anim: DriverAnimation, speed: int, interval: int, base_value: float):
    driver_anim.expressions.append(f"int(frame / {interval})*{speed}")
    driver_anim.base_value = base_value

# update linearly, vertex scrolling
def update_driver_linear(driver_anim: DriverAnimation, speed: float, base_value: float):
    driver_anim.expressions.append(f"frame*{speed}")
    driver_anim.base_value = base_value

# update with sin, vertex scrolling
# in game formula is amp * frequency * cos((frame * frequency + offset) * angle_conversion_factor) * 32
# 32 and the conversion factor are unique to sm64 and UV coordinates being s10.5, which won't be needed here
def update_driver_sinusoidal(driver_anim: DriverAnimation, amplitude: float, frequency: float, offset: float, base_value: float):
    driver_anim.expressions.append(f"cos(radians(frame*{frequency} + {offset}))*{amplitude}*{frequency}*32")
    driver_anim.base_value = base_value

# update with noise, vertex scrolling
# uses modifier, needs to be cleaned up later
def update_driver_noise(driver: bpy.types.Driver, amplitude: float, base_value: float):
    mod = driver.modifiers.new("NOISE")
    mod.Strength = amplitude


def remove_driver_modifiers(driver: bpy.types.Driver):
    [driver.modifiers.remove(mod) for mod in driver.modifiers]

