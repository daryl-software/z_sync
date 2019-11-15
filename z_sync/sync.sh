#!/bin/bash

#sudo sysctl -w fs.inotify.max_user_watches=524288
sudo lsyncd --nodaemon /Volumes/Work/2lm/z_sync/config.lua

