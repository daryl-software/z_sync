# Install / Update project
```
git submodule foreach --recursive git submodule update --init 
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
git submodule add ssh://git@gitlab.easyflirt.com:222/dating/v4.git v4
```