import json
from datetime import datetime

import numpy as np


class TimeMeasurement:
    def __init__(self):
        self.start = datetime.now()
        self.durations = {}

    def run_function(self, function, *props):
        start = np.datetime64("now")
        result = function(*props)
        duration = (np.datetime64("now") - start).item().total_seconds()
        try:
            self.durations[function.__name__] = np.insert(
                self.durations[function.__name__], 0, duration
            )
        except KeyError:
            self.durations[function.__name__] = [duration]
        return result

    def print_durations(self, name, other={}):
        for function_name, durations in self.durations.items():
            print(f"{name}: {function_name}: {np.average(durations)} seconds")
        for function_name, duration in other.items():
            print(f"{name}: {function_name}: {duration}")

    def save_durations_to_file(self, results_folder, folder_name, other={}):
        results = {}
        for function_name, durations in self.durations.items():
            results[function_name] = f"{np.average(durations)} seconds"
        for function_name, duration in other.items():
            results[function_name] = f"{duration}"
        with open(f"{results_folder}/results/{folder_name}/durations.txt", "w") as file:
            json.dump(results, file)
