//
//  Rsync.swift
//  iSync
//
//  Created by Florian Morello on 07/10/15.
//  Copyright © 2015 Florian Morello. All rights reserved.
//

import Foundation

@objc protocol RsyncDelegate: class {
    @objc optional func rsyncUpdate(for path: String, msg: String)
    @objc optional func rsyncError(for path: String, msg: String)
    @objc optional func rsyncComplete(for path: String)
}

class Rsync {
    weak var delegate: RsyncDelegate?
    
    let rsyncPath: String = "/usr/local/bin/rsync"
    let source: String
    let destination: String
    
    let operationQueue = OperationQueue()
    var queuedPaths: Set<String> = []
    
	var defaultParams = [
		"-avh",
		"-e ssh",
	]
    
    init(config: App.Config) {
        source = config.source
        destination = config.target

        if config.rsync.dryRun == true {
            defaultParams.append("--dry-run")
        }
        if config.rsync.ignoreErrors == true {
            defaultParams.append("--ignore-errors")
        }
        if config.rsync.checksum == true {
            defaultParams.append("--checksum")
        }
        if config.rsync.compress == true {
            defaultParams.append("--compress")
        }
        if config.rsync.inPlace == true {
            defaultParams.append("--inplace")
        }
        if config.rsync.delete == true {
            defaultParams.append("--delete")
        }

        config.rsync.excludes?.forEach {
            defaultParams.append("--exclude=\($0)")
        }
        
        operationQueue.maxConcurrentOperationCount = 1
    }

    internal func toggleParam(_ name: String, add: Bool) {
        let io = defaultParams.firstIndex(of: name)
        if add == false && io != nil {
            defaultParams.remove(at: io!)
        } else if add == true && io == nil {
            defaultParams.append(name)
        }
    }

    
    func sync(paths: [String]) {
        let unique = Array(Set(paths))
        //        print(paths)
        //        print(unique)
        let filtered = unique.filter { path in
            return path.range(of: #"/\.(idea|git)/"#, options: .regularExpression) == nil
                && path.range(of: #"___jb_(tmp|old|bak)___"#, options: .regularExpression) == nil
                && path.range(of: #"\.(DS_Store|AppleDouble|settings|buildpath|project)"#, options: .regularExpression) == nil
        }
        guard !filtered.isEmpty else {
            return
        }
        let relatives = filtered.compactMap { $0.replacingOccurrences(of: source, with: "") }
        relatives.sorted().forEach { path in
            print("Rsync \(path) ⏱ scheduled")
            sync(path: path)
        }
    }

    func sync(path: String) {
        guard queuedPaths.contains(path) == false else {
            print("Rsync \(path) 🙃 already queued to rsync")
            return
        }
        queuedPaths.insert(path)
        
        var params: [String] = self.defaultParams
        params.append(self.source + path)
        params.append(self.destination + path)
        
        let stdo = Pipe()
        let errorPipe = Pipe()
        
        let process = Process()
        process.launchPath = self.rsyncPath
        process.arguments = params
        process.standardOutput = stdo
        process.standardError = errorPipe
        
        let ope = AsyncProcessOperation(process: process, starting: { [weak self] in
            guard let self = self else { return }
            print("Rsync \(self.rsyncPath) \(params.joined(separator: " "))")
            self.queuedPaths.remove(path)
        })
        stdo.fileHandleForReading.readabilityHandler = { [weak self] fh in
            if let str = String(data: fh.availableData, encoding: String.Encoding.utf8)?.trimmed(), !str.isEmpty {
                str.components(separatedBy: "\n").forEach {
                    print("Rsync \(path) ⚡️ \($0)")
                }
                self?.delegate?.rsyncUpdate?(for: path, msg: str)
            }
        }
        errorPipe.fileHandleForReading.readabilityHandler = { [weak self] fh in
            if let str = String(data: fh.availableData, encoding: String.Encoding.utf8)?.trimmed(), !str.isEmpty {
                str.components(separatedBy: "\n").forEach {
                    print("Rsync \(path) 🤬 \($0)")
                }
                self?.delegate?.rsyncError?(for: path, msg: str)
            }
        }
        process.terminationHandler = { [weak self] ref in
            print("Rsync \(path) ✅")
            (ref.standardOutput as? Pipe)?.fileHandleForReading.readabilityHandler = nil
            (ref.standardError as? Pipe)?.fileHandleForReading.readabilityHandler = nil
            self?.delegate?.rsyncComplete?(for: path)
            ope.state = .finished
        }
        
        operationQueue.addOperation(ope)
	}
}

class AsyncProcessOperation: AsynchronousOperation {
    let process: Process
    let startCallback: () -> Void
    
    init(process: Process, starting: @escaping () -> Void) {
        self.process = process
        self.startCallback = starting
        
    }
    
    override func main() {
        super.main()
        
        guard state == .executing else { return }
        
        startCallback()
        process.launch()
    }
}

class AsynchronousOperation: Operation {
    override var isAsynchronous: Bool {
        return true
    }
    
    override var isExecuting: Bool {
        return state == .executing
    }
    
    override var isFinished: Bool {
        return state == .finished
        
    }
    
    var state = State.ready {
        willSet {
            willChangeValue(forKey: state.keyPath)
            willChangeValue(forKey: newValue.keyPath)
        }
        didSet {
            didChangeValue(forKey: state.keyPath)
            didChangeValue(forKey: oldValue.keyPath)
        }
    }
    
    enum State: String {
        case ready = "Ready"
        case executing = "Executing"
        case finished = "Finished"
        fileprivate var keyPath: String { return "is" + self.rawValue }
    }
    
    override func start() {
        if self.isCancelled {
            state = .finished
        } else {
            state = .ready
            main()
        }
    }
    
    override func main() {
        if self.isCancelled {
            state = .finished
        } else {
            state = .executing
        }
    }
}
