import threading
from multiprocessing import Process
import time


class ThreadsManagement:
    def __init__(self):
        self.threads = []

    def add_and_start(self, target=None, args=None):
        thread = threading.Thread(target=target, args=args)
        thread.start()
        self.threads.append(thread)
        return thread

    def join(self):
        for th in self.threads:
            th.join()


class ProcessesManagement:
    def __init__(self, max_processes=3):
        self.processes = []
        self.waiting_processes = []
        self.running_processes = []
        self.max_processes = max_processes

    def add_waiting(self, target=None, args=None):
        if args is None:
            self.waiting_processes.append(Process(target=target))
        else:
            self.waiting_processes.append(Process(target=target, args=args))

    def add_and_start(self, target=None, args=None):
        process = Process(target=target, args=args)
        process.start()
        self.running_processes.append(process)

    def get_next_process(self):
        try:
            return self.waiting_processes.pop(0)
        except IndexError:
            return None

    def wait_for_process(self):
        process_removed = False
        while not process_removed:
            for index, running_process in enumerate(self.running_processes):
                if not running_process.is_alive():
                    self.running_processes.pop(index)
                    process_removed = True
                    break
            if not process_removed:
                time.sleep(60)

    def run_all(self):
        self.running_processes = []
        next_process = self.get_next_process()

        while next_process is not None:
            next_process.start()
            self.running_processes.append(next_process)
            if len(self.running_processes) >= self.max_processes:
                self.wait_for_process()
            next_process = self.get_next_process()

        if len(self.running_processes) > 0:
            for running_process in self.running_processes:
                running_process.join()
