from helper_functions import try_make_dir
from simulation import Simulation, AntOrientationType

my_results_folder_dir = "/home/katka/Learning"  # TODO: change this to your folder
simulation_name = "simple_example_1"

try_make_dir(my_results_folder_dir + "/results")

if __name__ == "__main__":
    simulation = Simulation(
        number_of_steps=100,
        settings={},
        random_variable_values=None,
        results_folder=my_results_folder_dir,
        simulation_name=simulation_name,
        simulation_folder_name=simulation_name,
        ant_orientation_type=AntOrientationType.TWO_PHEROMONES,
    )
    simulation.run_simulation()
    simulation.draw_results([100])  # By default, we save pheromones every 100th step
