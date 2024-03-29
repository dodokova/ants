import json

from save_results.draw_step import draw_step
from helper_functions import try_make_dir
from settings import Settings


def draw_results(
    simulation_name: str,
    results_folder: str,
    number_of_steps: int,
    additional_settings: dict = {},
    step_diff: int = 100,
):
    with open(f"{results_folder}/results/{simulation_name}/settings.py") as file:
        settings_from_file = json.loads(file.read())
        settings = Settings({**settings_from_file, **additional_settings})

    drawings_folder_name = "drawings"
    try_make_dir(
        results_folder + "/results/" + simulation_name + "/" + drawings_folder_name
    )

    steps = list(range(step_diff, number_of_steps + 1, step_diff))

    for step in steps:
        draw_step(
            f"{results_folder}/results/{simulation_name}",
            drawings_folder_name,
            step,
            settings,
        )
