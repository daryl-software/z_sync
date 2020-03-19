# Z Sync

This tool run in background and watch FS events to trigger sync (via rsync) from local directories to remote server.

Syncs are batched to limit triggers, by default every 0.5sec.

Reads config files in this order :
1. `config.yaml.default`
2. `config.yaml` or file specified by `--config` parameter
3. `~/.z_sync.yaml`

```bash
cd z_sync
pip3 install --user -r requirements.txt --upgrade
cp config.yaml.default config.yaml
vim config.yaml
./sync.py [--debug] [--init] [--from-server|local] 
```

Tip: `ctrl+z` to trigger a full sync.

A CLI is available to force sync from or to remote server. Type `help`.

