settings {
    logfile = "/tmp/z_sync.log",
    statusFile = "/tmp/z_sync_status.log",
    statusInterval = 1
}

sync {
    default.rsync,
    source="/home/gregory/Data/Lab/",
    target="gregory@lab.easyflirt.com:/data/users/gregory",
    excludeFrom="/home/gregory/Data/Lab/2lm/z_sync/lsyncd.exclude",
    rsync = {
        binary = "/usr/bin/rsync",
        compress = false,
        verbose = true,
        archive = true,
    },
    exclude = {},
    delay=0
}
