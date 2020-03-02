#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 noexpandtab:

import time
import threading
import os
import sys
import re
import logging
import termcolor
import signal
import argparse
import yaml
import ntfy

# pip3 install --user MacFSEvents
from fsevents import Observer, Stream


class Syncer:
    def __init__(self, config, disable_notifications):
        self.config = config
        self.threads = {}
        self.excludes = []
        self.notifications = not disable_notifications
        logging.getLogger("ntfy").setLevel(logging.WARNING)
        for ex in self.config["excludes"]:
            self.excludes.append(re.compile(ex))
        self.rsync_ops = self.config["rsync_opts"]
        for ex in self.config["rsync_excludes"]:
            self.rsync_ops += " '--exclude=%s'"%ex
        self.path_chunks = []
        self.chunk_time = None
        self._stop = False
        self._lock = threading.Lock()
        self._thread = threading.Thread(name="interval", target=self.tick)
        self._thread.start()

    def tick(self):
        while not self._stop:
            if self.chunk_time is None:
                self.chunk_time = time.time()
            if time.time() - self.chunk_time >= 0.5 and len(self.path_chunks) > 0:
                self._lock.acquire(True)
                for path in self.optimize_paths():
                    if not path in self.threads:
                        th = threading.Thread(name="Sync-%s" % path, target=self.sync, args=(path,))
                        self.threads[path] = th
                        th.start()
                self.chunk_time = None
                self.path_chunks.clear()
                self._lock.release()
            else:
                time.sleep(0.1)

    def sync(self, path):
        if not path.endswith("/"):
            path = path + "/"
        for ex in self.excludes:
            if ex.match(path):
                logging.info("EXCLUDED: %s" % path)
                return

        if self.notifications:
            ntfy.notify(title="🚣 Sync in progress", message="📂 %s"%path)
        logging.info("Sync for path %s has started", path)
        args = (self.config["rsync"], self.rsync_ops, "'%s'"%path, "'%s'"%(self.config["path_dest"] + path.replace(self.config["path_source"], "")))
        logging.debug("RSYNC: %s", (" ".join(args)))
        ret = os.system(" ".join(args))
        if ret > 0:
            logging.warning("Sync for path %s has FAILED with error code %s", path, ret)
            if self.notifications:
                ntfy.notify(title="💢 FAILED 💢", message="'%s' sync failed with error=%s"%(path, ret))
        else:
            logging.info("Sync for path %s has finished (%s)", path, ret)
            if self.notifications:
                ntfy.notify(title="🍻 Sync DONE 👍", message="📂 %s"%path)

    def cleanup(self, all=False):
        if all:
            self._stop = True
            self._thread.join(2)
        cleanup_threads = []
        for th in self.threads:
            try:
                self.threads[th].join(0.0)
            except RuntimeError: pass
            if not self.threads[th].is_alive():
                logging.debug("Thread %s has been reaped" % self.threads[th].name)
                cleanup_threads.append(th)
        for th in cleanup_threads:
            del self.threads[th]

    def callback(self, path: str, mask):
        self.cleanup()
        if "/.git/" in path:
            path = re.sub(r'/\.git/.*', '', path)

        if not path in self.path_chunks:
            self._lock.acquire(True)
            self.path_chunks.append(path)
            self._lock.release()

    def optimize_paths(self):
        self.path_chunks.sort()
        cur = None
        for path in self.path_chunks:
            if cur is None:
                cur = path
            elif path.startswith(cur):
                continue
            else:
                cur = path
            yield path

    def sig_handler(self, signum, frame):
        self.sync(self.config["path_source"])


def setup_logging(debug_level=None, threadless=False, logfile=None, rotate=False):  # {{{
    # if threadless mode, it's a workarround for new Process
    if threadless or rotate:
        try:
            logfile = logging.root.handlers[0].baseFilename

            if rotate:
                try:
                    logging.root.handlers[0].close()
                # rotate handled by logrotate
                except:
                    logging.info("Unable to close file:")
                    logging.info(sys.exc_info()[1])
        except AttributeError:
            logfile = None

        # removing them with technic to not need lock :
        # see line 1198 from /usr/lib/python2.6/logging/__init__.py
        while len(logging.root.handlers) > 0:
            logging.root.handlers.remove(logging.root.handlers[0])

        if debug_level is None:
            debug_level = logging.root.getEffectiveLevel()
    else:
        # ensure closed
        logging.shutdown()
        if debug_level is None:
            debug_level = logging.DEBUG

    if logfile:
        loghandler = logging.handlers.WatchedFileHandler(logfile)
    else:
        loghandler = logging.StreamHandler()

    loghandler.setLevel(logging.DEBUG)
    # loghandler.setFormatter(logging.Formatter(logformat, logdatefmt))
    use_color = False
    if "TERM" in os.environ and (re.search("term", os.environ["TERM"]) or os.environ["TERM"] in ('screen',)):
        use_color = True
    loghandler.setFormatter(ColoredFormatter(use_color))

    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[0])

    logging.root.addHandler(loghandler)
    logging.root.setLevel(debug_level)

class ColoredFormatter(logging.Formatter):  # {{{
    COLORS = {
        'WARNING': 'yellow',
        'INFO': 'cyan',
        'CRITICAL': 'white',
        'ERROR': 'red'
    }
    COLORS_ATTRS = {
        'CRITICAL': 'on_red',
    }

    def __init__(self, use_color=True):
        # main formatter:
        logformat = '%(asctime)s %(levelname)-8s %(message)s'
        logdatefmt = '%H:%M:%S %d/%m/%Y'
        logging.Formatter.__init__(self, logformat, logdatefmt)

        # for thread-less scripts :
        logformat = '%(asctime)s %(levelname)-8s %(message)s'
        self.mainthread_formatter = logging.Formatter(logformat, logdatefmt)

        self.use_color = use_color
        if self.use_color and not 'termcolor' in sys.modules:
            try:
                import termcolor
            except:
                self.use_color = False
                logging.debug("You could activate colors with 'termcolor' module")

    def format(self, record):
        if self.use_color and record.levelname in self.COLORS:
            if record.levelname in self.COLORS_ATTRS:
                record.msg = '%s' % termcolor.colored(record.msg, self.COLORS[record.levelname],
                                                      self.COLORS_ATTRS[record.levelname])
            else:
                record.msg = '%s' % termcolor.colored(record.msg, self.COLORS[record.levelname])
        if threading.currentThread().getName() == 'MainThread':
            return self.mainthread_formatter.format(record)
        else:
            return logging.Formatter.format(self, record)



if __name__ == "__main__":
    setup_logging(logging.INFO)

    parser = argparse.ArgumentParser(
        description="Sync a volume from OSX to Linux server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true", help="DEBUG")
    parser.add_argument("--init", action="store_true", help="Sync first")
    parser.add_argument("--disable-notifications", action="store_true", help="Disable notifications")
    parser.add_argument("--config", action="store", default="config.yaml", help="Use a config file rather than default config.yml")
    args = parser.parse_args()

    if args.debug:
        logging.root.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    with open(args.config, "r") as configfile:
        config = yaml.load(configfile, Loader=yaml.FullLoader)
        
    observer = Observer()
    syncer = Syncer(config, args.disable_notifications)

    if args.init:
        logging.info("--------- Init Sync -----------")
        syncer.sync(config["path_source"])

    # CTRL+Z will force a full sync :
    signal.signal(signal.SIGTSTP, syncer.sig_handler)

    observer.start()
    logging.info("------- FS WATCHING %s -------" % config["path_source"])
    logging.info("(CTRL+z to force a full sync)")

    os.chdir(config["path_source"])
    stream = Stream(syncer.callback, config["path_source"])
    try:
        observer.schedule(stream)
        observer.join()
        logging.info("Schedule finished")
    except KeyboardInterrupt:
        logging.warning("CTRL+c")
    finally:
        logging.info("Stopping observer...")
        observer.stop()
        logging.debug("Cleanup threads ...")
        syncer.cleanup(True)
        logging.info("Finished.")
