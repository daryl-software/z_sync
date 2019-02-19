# 2LM Meta project


## Install
```bash
git submodule update --init
git submodule foreach 'test -e composer.json && composer install --ignore-platform-reqs || true'
git submodule foreach 'test -e package.json && npm install --ignore-platform-reqs || true'
```

## Update projects
```bash
git submodule foreach git pull --rebase
```

## Outdated deps
```bash
git submodule foreach 'test -e composer.json && composer outdated -D || true'
git submodule foreach 'test -e package.json && npm outdated || true'
```

## Grep files
```bash
# grep php files
ackgrep --php expression

# grep all files
ackgrep expression
```

## Adding a project
```bash
git submodule add ssh://git@gitlab.easyflirt.com:222/prelinker-click-logger/bridghit.git bridghit
```