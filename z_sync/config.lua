settings {
    logfile = "/tmp/z_sync.log",
    statusFile = "/tmp/z_sync_status.log",
    statusInterval = 1
}

sync {
    default.rsync,
    source="/Volumes/Work/",
    target="gregory@lab.easyflirt.com:/data/users/gregory",
    excludeFrom="/Volumes/Work/2lm/z_sync/lsyncd.exclude",
    rsync = {
        binary = "/usr/local/bin/rsync",
        compress = false,
        verbose = true,
        archive = true,
    },
    exclude = {},
    delay=0
}
