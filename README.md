# 2LM Meta project

## Command shortcuts
@see package.json/scripts entry

## Z Sync

Cet outil tourne en background et écoute les modifications faites sur le système de fichier local, aggrège et temporise (0.5s) avant de lancer une synchro du dossier contenant les fichiers modifiés (via rsync) sur le serveur distant (lab).

```bash
cd z_sync
pip3 install --user -r requirements.txt
vim config.yaml
./sync.py [--debug] [--init] [--from-server|local] 
```

Tip: `ctrl+z` pour lancer une synchro full.
