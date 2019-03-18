settings {
    logfile = "z_sync/sync.log",
    statusFile = "z_sync/status.log",
    statusInterval = 1
}

sync {
    default.rsync,
    source="/Volumes/Work/2lm/",
    target="florian@lab.easyflirt.com:/data/users/florian/code",
    excludeFrom="/Volumes/Work/2lm/z_sync/lsyncd.exclude",
    rsync = {
        binary = "/usr/local/bin/rsync",
        compress = true,
        verbose = true,
        archive = true,
    },
    exclude = {},
    delay=0
}