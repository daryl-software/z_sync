import inotify.adapters
import threading
import time

class Observer(threading.Thread):
    def __init__(self):
        self.stream = None
        self.__stop = threading.Event()
        self.i = None
        threading.Thread.__init__(self)

    def run(self):
        while self.stream is None and not self.__stop.is_set():
            time.sleep(0.2)
        while not self.__stop.is_set():
            print("tick")
            for event in self.i.event_gen(timeout_s=1):
                try:
                    if event is not None:
                        print(event)
                except:
                    logging.warning("error", exc_info=True)
        print("DONE")

    def stop(self):
        print("STOP ASKED")
        self.__stop.set()

    def schedule(self, stream):
        self.stream = stream
        self.i = inotify.adapters.InotifyTree(stream.get_path())

class Stream:
    def __init__(self, callback, path):
        self.callback = callback
        self.path = path

    def get_path(self):
        return self.path

    def callback(self):
        return self.callback


