import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from threading import Thread
from queue import Queue
import time
import random
from threading import Thread

NUM_TASKS_TO_ADD = 10  # Define the number of tasks to be added to the queue

class TaskQueue(Queue):

    def __init__(self, num_workers=1):
        Queue.__init__(self)
        self.num_workers = num_workers
        logging.debug(f"Initializing TaskQueue with {self.num_workers} workers.")
        self.start_workers()

    def add_task(self, task, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))
        logging.debug(f"Task added: {task.__name__} with args: {args} and kwargs: {kwargs}")

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()
            logging.debug(f"Worker {i} started.")

    def worker(self):
        while True:
            item, args, kwargs = self.get()
            logging.debug(f"Worker executing task: {item.__name__} with args: {args} and kwargs: {kwargs}")
            item(*args, **kwargs)  
            self.task_done()
            logging.debug(f"Task {item.__name__} completed.")


def add_tasks_at_random_intervals(queue, task, min_ms=50, max_ms=1000):
    for _ in range(NUM_TASKS_TO_ADD):
        time.sleep(random.randint(min_ms, max_ms) / 1000.0)
        queue.add_task(task, *args, **kwargs)
        logging.debug(f"Task {task.__name__} scheduled to be added to the queue.")
    print(f"Added {NUM_TASKS_TO_ADD} tasks to the queue.")

def tests():
    def blokkah(*args, **kwargs):
        time.sleep(1)
        print("Blokkah mofo!")

    q = TaskQueue(num_workers=5)

    # Start a thread to add tasks at random intervals
    task_adder = Thread(target=add_tasks_at_random_intervals, args=(q, blokkah))
    task_adder.daemon = True
    task_adder.start()

    q.join()       # block until all tasks are done
    print("All done!")

    # Ensure that the number of completed tasks matches the expected number
    assert q.unfinished_tasks == 0, f"Expected all tasks to be completed, but {q.unfinished_tasks} tasks remain."
    logging.debug("All tasks have been completed.")

if __name__ == "__main__":
    tests()
