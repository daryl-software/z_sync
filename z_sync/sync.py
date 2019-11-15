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

# pip3 install --user MacFSEvents
from fsevents import Observer, Stream

# Configuration :
PATH_SOURCE = "/Volumes/Work/"
PATH_DEST = "gregory@lab.easyflirt.com:/data/users/gregory/"
RSYNC = "/usr/local/bin/rsync"
RSYNC_OPTS = "-rlpt --delete"
EXCLUDES = [
    r'\..+?/',
    r'/Storage/'
]
RSYNC_EXCLUDES = [
    "/.Spotlight-V100/",
    "/.Trashes/",
    "/.fseventsd/",
    "/Storage/"
]


class Syncer:
    def __init__(self):
        self.threads = {}
        self.excludes = []
        for ex in EXCLUDES:
            self.excludes.append(re.compile(ex))
        self.rsync_ops = RSYNC_OPTS
        for ex in RSYNC_EXCLUDES:
            self.rsync_ops += " '--exclude=%s'"%ex

    def sync(self, path):
        for ex in self.excludes:
            if ex.match(path):
                logging.info("EXCLUDED: %s" % path)
                return
        logging.info("Sync for path %s has started", path)
        args = (RSYNC, self.rsync_ops, "'%s'"%path, "'%s'"%(PATH_DEST + path.replace(PATH_SOURCE, "")))
        logging.debug("RSYNC: %s", (" ".join(args)))
        ret = os.system(" ".join(args))
        if ret > 0:
            logging.warning("Sync for path %s has FAILED with error code %s", path, ret)
        else:
            logging.info("Sync for path %s has finished (%s)", path, ret)

    def cleanup(self):
        cleanup_threads = []
        for th in self.threads:
            self.threads[th].join(0.0)
            if not self.threads[th].is_alive():
                logging.debug("Thread %s has been reaped" % self.threads[th].name)
                cleanup_threads.append(th)
        for th in cleanup_threads:
            del self.threads[th]

    def callback(self, path: str, mask):
        self.cleanup()
        if "/.git/" in path:
            path = re.sub(r'/\.git/.*', '', path)

        if not path in self.threads:
            th = threading.Thread(name="Sync-%s" % path, target=self.sync, args=(path,))
            self.threads[path] = th
            th.start()


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

    loghandler.setLevel(debug_level)
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
    setup_logging()
    observer = Observer()
    syncer = Syncer()
    logging.info("--------- Init Sync -----------")
    syncer.sync(PATH_SOURCE)
    observer.start()
    logging.info("------- FS WATCHING %s -------" % PATH_SOURCE)
    os.chdir(PATH_SOURCE)
    stream = Stream(syncer.callback, PATH_SOURCE)
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
        syncer.cleanup()
        logging.info("Finished.")
