from threading import Thread
from queue import Queue
import time
import random
from threading import Thread

class TaskQueue(Queue):

    def __init__(self, num_workers=1):
        Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()

    def add_task(self, task, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            item, args, kwargs = self.get()
            item(*args, **kwargs)  
            self.task_done()


def add_tasks_at_random_intervals(queue, task, min_ms=50, max_ms=1000):
    while True:
        time.sleep(random.randint(min_ms, max_ms) / 1000.0)
        queue.add_task(task)

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

if __name__ == "__main__":
    tests()
