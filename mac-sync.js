const fsevents = require('fsevents');
const path = require('path');
const rsync = require('rsync');
const config = require('./z_sync/config');

const folderRegex = new RegExp('^(' + config.folders.join('|') + ')');
function ignore(path) {
    if (path.match(/\.(idea\/|git\/|DS_Store|AppleDouble)/)) {
        return true;
    }
    if (path.match(/___jb_(old|tmp|bak)___/)) {
        return true;
    }
    if (path.match(/\.sw[px]$/)) {
        return true;
    }

    return false;
}

function changed(thepath, info) {
    if (ignore(thepath)) {
        // ignored regex
        return;
    }

    const relative = path.relative(__dirname, thepath);
    if (!relative.match(folderRegex)) {
        // ignored path
        // console.log('skipped', relative);
        return;
    }
    console.info('file changed', relative);
    enqueue(path.dirname(relative))
}

function enqueue(folder) {
    if (queued.indexOf(folder) === -1) {
        let found = false;
        for (const old of queued) {
            if (folder.indexOf(old) === 0) {
                console.log('parent already in queue');
                found = true;
                break;
            }
        }
        if (found) {
            return;
        }
        queued.push(folder);
        queued.sort();

        console.log('queue', queued);
        sync();
    }
}

function sync() {
    const folder = queued.pop();

    var rs = new rsync()
        // .dry()
        .shell('ssh')
        .flags('avh')
        .compress()
        .set('ignore-errors')
        .set('checksum')
        .set('exclude-from', 'z_sync/exclude.txt')
        .delete()
        .source(__dirname + '/' + folder)
        .destination('florian@lab.easyflirt.com:~/' + folder)
    ;
    rs.execute(function(error, code, cmd) {
        console.log('rsync finished', error, code, cmd);
    }, function(data){
        console.debug(data.toString('utf8'));
    }, function(data) {
        console.error(data);
    });
}

console.info('Watching file change in ' + __dirname);

/**
 * Queued folder to sync
 * @type {Array}
 */
var queued = [];

var watcher = fsevents(__dirname);
watcher.on('change', changed);
watcher.start(); // To start observation
// watcher.stop()  // To end observation