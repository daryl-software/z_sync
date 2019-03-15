const fsevents = require('fsevents');
const path = require('path');
const rsync = require('rsync');
const config = require('./z_sync/config');
const Queue = require('promise-queue');
const { createLogger, format, transports } = require('winston');


const folderRegex = new RegExp('^(' + config.folders.join('|') + ')');
let level = 'info';
let vRegex = new RegExp(/^-([v]{1,})$/);
let mRegex = new RegExp(/--sync=([a-z0-9_\-]+)/);
var queued = [];
var queue = new Queue(1, Infinity);

process.argv.forEach((arg) => {
   if (arg.match(vRegex)) {
       let match = arg.match(vRegex);
       let n = match[1].length;
       if (n >= 3) {
           level = 'silly';
       } else if (n >= 2) {
           level = 'debug';
       } else if (n >= 1) {
           level = 'verbose';
       }
   } else if (arg.match(mRegex)) {
       let match = arg.match(mRegex);
       if (match[1].match(folderRegex)) {
           queued.push(match[1]);
       }
   }
});

const logger = createLogger({
    level: level,
    format: format.combine(
        format.colorize(),
        format.splat(),
        format.simple()
    ),
    transports: [
        new transports.Console(),
    ]
});

logger.silly(folderRegex);

if (queued.length) {
    queue.add(sync);
}

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

function changed(thepath) {
    logger.silly('file changed ' + thepath);
    if (ignore(thepath)) {
        logger.debug('ignored change in ' + thepath);
        return;
    }

    const relative = path.relative(__dirname, thepath);
    if (!relative.match(folderRegex)) {
        // ignored path
        logger.debug('skipped ' + relative);
        return;
    }
    logger.info('file changed ' + relative);
    enqueue(path.dirname(relative) + '/')
}

function enqueue(folder) {
    if (queued.indexOf(folder) === -1) {
        let found = false;
        for (const old of queued) {
            if (folder.indexOf(old) === 0) {
                logger.debug('parent already in queue');
                found = true;
                break;
            }
        }
        if (found) {
            return;
        }
        queued.push(folder);
        queued.sort();

        logger.debug('queuing sync ' + folder);
        queue.add(sync);
    }
}

function sync() {
    const folder = '/' + queued.pop();
    logger.debug('[' + folder + '] rsync start');
    var rs = new rsync()
            .shell('ssh')
            .flags('avh')
            .compress()
            .set('ignore-errors')
            .set('checksum')
            .set('exclude-from', 'z_sync/exclude.txt')
            .delete()
            .source(__dirname + folder)
            .destination('lab.easyflirt.com:~' + folder)
    ;
    rs.execute(function(error, code, cmd) {
        logger.info('Done syncing ' + folder);
        // logger.debug('rsync finished', error, code, cmd);
    }, function(data){
        // progress
        // output += data.toString('utf8');
    }, function(data) {
        logger.error(data);
    });
}

logger.info('Watching file change in ' + __dirname);

/**
 * Queued folder to sync
 * @type {Array}
 */

var watcher = fsevents(__dirname);
watcher.on('change', changed);
watcher.start(); // To start observation
// watcher.stop()  // To end observation