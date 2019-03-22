# 2LM Meta project

## Sync
```bash
brew install lsyncd
sudo z_sync/sync.sh
```

## Clone all repos
```bash
npm run clone
```

## Update projects
```bash
npm run pull
```

## Outdated deps
```bash
git submodule foreach 'test -e composer.json && composer outdated -D || true'
git submodule foreach 'test -e package.json && npm outdated || true'
```

## Grep files
```bash
# grep php files
ack --php expression

# grep all files
ack expression
```
