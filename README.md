# Simulator of collective behavior in ats

To run simulations, set up your virtual environment and install dependencies from `requirements.txt`.

## Simple simulation

Use class `Simulation` to run one simulation.
You can set up:

- number of steps, where each step represents 0.5 seconds by default
- settings - modify model variables from class `Settings`
- ant orientation type
  - two pheromones
  - one pheromone
  - one pheromone + orientation

You can find an example in `script_example_simple.py`.

## Simulation Group

You can create a group of simulations with different parameters to compare their impact using `SimulationGroup`.
All simulations from the group use the same random variable values.
Simulation group can be run multiple times (property `repetitions`).

You can find an example in `script_example.py`.
