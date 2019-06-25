//
//  App.swift
//  swiftSync
//
//  Created by Florian Morello on 11/06/2019.
//  Copyright © 2019 Florian Morello. All rights reserved.
//

import Foundation

class App: DirectoryMonitorDelegate, RsyncDelegate {
    struct Config: Decodable {
        let source: String
        let target: String

        let rsync: RsyncConfig

        struct RsyncConfig: Decodable {
            let excludes: [String]?
            let dryRun: Bool?
            let inPlace: Bool?
            let ignoreErrors: Bool?
            let checksum: Bool?
            let delete: Bool?
            let compress: Bool?
        }
    }

    let rsync: Rsync
    let fileMonitor: DirectoryMonitor
    
    let source: String
    let destination: String
    
    init(config: Config) {
        source = config.source
        destination = config.target
        rsync = Rsync(config: config)
        
        fileMonitor = DirectoryMonitor(paths: [source], latency: 0.6)

        print("Source: \(source)")
        print("Destination: \(destination)")
    }
    
    func start() {
        rsync.delegate = self
        fileMonitor.delegate = self
        rsync.sync(path: "")
    }
    
    func pathsDidChange(_ paths: [String]) {
        rsync.sync(paths: paths)
    }
    
    func rsyncComplete(for path: String) {        
        if fileMonitor.started == false && path == "" {
            print("Rsync complete")
            print("Start watching for changes in \(self.source)")
            self.fileMonitor.start()
        }
    }
}
