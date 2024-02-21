import json
import math
from decimal import *

import numpy as np
from PIL import Image, ImageDraw


def draw_circle(draw, x, y, r, **kwargs):
    return draw.ellipse([(x - r), (y - r), (x + r), (y + r)], **kwargs)


def position_for_picture(x, settings):
    return (Decimal(x) / settings.NUMERICAL_STEP_SIZE) * settings.ZOOM


def draw_foods(draw, foods, settings, step):
    for food in foods:
        if (
            int(food["amount"]) > 0
            and food["created_at"] <= step
            and (food["removed_at"] is None or food["removed_at"] >= step)
        ):
            draw_circle(
                draw,
                position_for_picture(food["x"], settings),
                position_for_picture(food["y"], settings),
                position_for_picture(food["radius"], settings),
                outline=(
                    round(204 * (1 - food["quality"])),
                    round(229 - (food["quality"] * 100)),
                    255,
                ),
                width=10,
            )


def draw_nest(draw, nest, settings):
    draw_circle(
        draw,
        position_for_picture(nest["x"], settings),
        position_for_picture(nest["y"], settings),
        position_for_picture(nest["radius"], settings),
        outline=(255, 165, 0),
        width=10,
    )


def draw_ant_position(draw, x, y, color, settings):
    draw_circle(
        draw,
        position_for_picture(x, settings),
        position_for_picture(y, settings),
        1,
        fill="#FF00BC",
        outline=color,
    )


def draw_ant_step(draw, ant, color, settings):
    # previous_x = Decimal(x) - (Decimal(math.cos(float(direction))) * settings.STEP_LENGTH)
    # previous_y = Decimal(y) - (Decimal(math.sin(float(direction))) * settings.STEP_LENGTH)
    draw.line(
        [
            position_for_picture(ant["previous_x"], settings),
            position_for_picture(ant["previous_y"], settings),
            position_for_picture(ant["x"], settings),
            position_for_picture(ant["y"], settings),
        ],
        fill=color,
    )


def draw_ants(draw, folder_path, step, settings):
    current_step = int(step)
    current_color_range = 0
    color_range_diff = int(150 / settings.NUMBER_OF_ANT_STEPS_IN_IMG)

    while (
        current_step >= 0 and step - current_step != settings.NUMBER_OF_ANT_STEPS_IN_IMG
    ):
        with open(f"{folder_path}/data/{current_step:05d}.txt", "r") as file:
            ants = json.loads(file.read())["ants"]
            color = "#{:02x}{:02x}{:02x}".format(
                current_color_range, current_color_range, current_color_range
            )
            green_color = "#{:02x}{:02x}{:02x}".format(
                current_color_range, current_color_range, current_color_range + 100
            )

            for ant_name, ant_data in ants.items():
                ant_move_color = color
                if (
                    ant_data["looking_for_food"] == "False"
                    or ant_data["looking_for_food"] is False
                ):
                    ant_move_color = green_color
                if (
                    current_step == 0
                    or (
                        ant_data["x"] == ant_data["previous_x"]
                        and ant_data["y"] == ant_data["previous_y"]
                    )
                    is None
                ):
                    draw_ant_position(
                        draw, ant_data["x"], ant_data["y"], color, settings
                    )
                else:
                    draw_ant_step(draw, ant_data, ant_move_color, settings)
        current_color_range += color_range_diff
        current_step -= 1


def generate_help_color_value(value, max_pheromone_value):
    if value is None:
        return 0
    if value <= 0.0:
        return 0

    color_value = Decimal(value) / Decimal(max_pheromone_value) * Decimal("180")
    return int(color_value)


def generate_hex_color_for_pheromones(
    pheromone_a, pheromone_b, max_pheromone_value_a, max_pheromone_value_b
):
    color_value_a = generate_help_color_value(pheromone_a, max_pheromone_value_a)
    color_value_b = generate_help_color_value(pheromone_b, max_pheromone_value_b)
    if color_value_a == 0 and color_value_b == 0:
        return None
    rgb_color = (
        255 - color_value_b,
        255 - (color_value_a + color_value_b),
        255 - color_value_a,
    )
    return rgb_color


def get_array_item_wo_error(array, i, j, default=0.0):
    try:
        return array[i][j]
    except IndexError:
        return default


def get_rectangle_position(i, j, zoom):
    return [
        max(0, int(math.floor(i * zoom - (zoom / 2)))),
        max(0, int(math.floor(j * zoom - (zoom / 2)))),
        int(math.ceil(i * zoom + (zoom / 2))),
        int(math.ceil(j * zoom + (zoom / 2))),
    ]


def draw_pheromones(draw, zoom, size, pheromone_1, pheromone_2=None):
    pheromone_1 = np.array(pheromone_1 or [0.0], dtype=float)
    max_pheromone_1 = np.amax(pheromone_1)
    pheromone_2 = np.array(pheromone_2 or [0.0], dtype=float)
    max_pheromone_2 = np.amax(pheromone_2)
    # max_pheromone_value = max(max_pheromone_1, max_pheromone_2)

    for i in range(size):
        for j in range(size):
            value_1 = get_array_item_wo_error(pheromone_1, i, j)
            value_2 = get_array_item_wo_error(pheromone_2, i, j)
            if value_1 != 0.0 or value_2 != 0.0:
                color = generate_hex_color_for_pheromones(
                    value_1, value_2, max_pheromone_1, max_pheromone_2
                )
                if color is not None:
                    draw.rectangle(
                        get_rectangle_position(i, j, zoom), outline=color, fill=color
                    )


def draw_step(simulation_folder, drawing_folder_name, step, settings):
    canvas = (
        settings.NUMERICAL_ARRAY_SIZE * settings.ZOOM,
        settings.NUMERICAL_ARRAY_SIZE * settings.ZOOM,
    )
    scale = 1
    thumb = canvas[0] / scale, canvas[1] / scale

    img = Image.new("RGBA", canvas, (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    with open(f"{simulation_folder}/data/{step:05d}.txt", "r") as file:
        data = json.loads(file.read())

    draw_pheromones(
        draw,
        settings.ZOOM,
        settings.NUMERICAL_ARRAY_SIZE,
        pheromone_1=data.get("pheromone_a"),
        pheromone_2=data.get("pheromone_b"),
    )
    draw_foods(draw, data.get("foods"), settings, step)
    draw_nest(draw, data.get("nest"), settings)
    draw_ants(draw, simulation_folder, step, settings)

    img.thumbnail(thumb)
    img.save(
        simulation_folder + "/" + drawing_folder_name + "/" + f"{step:05d}" + ".png"
    )
