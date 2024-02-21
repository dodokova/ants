from helper_functions import try_make_dir
from simulation import SimulationGroup

my_results_folder_dir = "/home/katka/Learning"  # TODO: change this to your folder

try_make_dir(my_results_folder_dir + "/results")

if __name__ == "__main__":
    # Settings for all simulations
    common_props = {
        "ANTS_NUMBER": 200,
        "AVAILABLE_ANTS": 100,
        "FOOD_SOURCES": [[220, 150, 15, 10000, 1, 0, None]],
        "NEST_POSITION": [80, 150, 20],
    }

    simulation_group = SimulationGroup(
        results_folder=my_results_folder_dir,
        group_props=common_props,
        group_name="test_example",
        number_of_steps=300,  # 1 step = 0.5 seconds
        repetitions=3,  # number of simulations with the same settings
        max_processes=5,  # number of simulations running in parallel
    )

    simulation_group.generate_random_variable_values()

    # Add simulations with different settings
    simulation_group.add_simulation(
        props={"ANTS_NUMBER": 200, "AVAILABLE_ANTS": 100},
        folder_name="n=200_an=100",
        simulation_name="Gauss",
    )
    simulation_group.add_simulation(
        props={"ANTS_NUMBER": 250, "AVAILABLE_ANTS": 50},
        folder_name="n=250_an=50",
        simulation_name="Nearest four points",
    )
    simulation_group.add_simulation(
        props={"ANTS_NUMBER": 300, "AVAILABLE_ANTS": 0},
        folder_name="n=300_an=0",
        simulation_name="Nearest grid point",
    )

    # Run all simulations 3 times
    # Each iteration runs with the same random variable values for all simulations
    # Results with images are saved in the results folder
    simulation_group.run_simulations(should_draw_results=True)
