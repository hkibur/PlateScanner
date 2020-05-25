import time
import threading
import collections

class CronJob(object):
    def __init__(self, interval, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.interval = interval
        self.last_time = -1

class ScannerCron(threading.Thread):
    def __init__(self, delta):
        super().__init__()
        self.delta = delta
        self.jobs = collections.OrderedDict()
        self.stop = True
        self.current_index = 0

    def add_job(self, *args, **kwargs):
        self.jobs[self.current_index] = CronJob(*args, **kwargs)
        self.current_index += 1
        return self.current_index - 1

    def del_job(self, index):
        del self.jobs[index]

    def start(self):
        self.stop = False
        super().start()

    def close(self):
        self.stop = True
        self.join()

    def cycle_cron(self):
        self.do_cron(True)

    def do_cron(self, force = False):
        now = time.time()
        for _, job in self.jobs.items():
            if now - job.last_time >= job.interval or force:
                job.last_time = now
                job.func(*job.args, **job.kwargs)
        cur_delta = time.time() - now
        if cur_delta < self.delta:
            time.sleep(self.delta - cur_delta)

    def run(self):
        while not self.stop:
            self.do_cron()
