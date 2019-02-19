# Install
```
git submodule  update --init
git submodule foreach 'composer install --ignore-platform-reqs || :'
git submodule foreach 'npm install --ignore-platform-reqs || :'
```

## Update projects
```
git submodule foreach git pull --rebase
```

## Grep in projects
Create a `~/.ackrc` file containing
```
--ignore-dir=.idea/
--ignore-dir=node_modules/
--ignore-dir=vendor/
--ignore-dir=bower_components/
--ignore-dir=bower_files/
```

Grep files
```bash
# grep php files
ackgrep --php expression

# grep all files
ackgrep expression
```

## Adding a project
```sh
git submodule add ssh://git@gitlab.easyflirt.com:222/prelinker-click-logger/bridghit.git bridghit
```