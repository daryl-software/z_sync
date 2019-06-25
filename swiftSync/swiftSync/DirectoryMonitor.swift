//
//  DirectoryMonitor.swift
//  iSync
//
//  Created by Florian Morello on 07/10/15.
//  Copyright © 2015 Florian Morello. All rights reserved.
//

import Foundation

protocol DirectoryMonitorDelegate: class {
	func pathsDidChange(_ paths: [String])
}

class DirectoryMonitor {
	weak var delegate: DirectoryMonitorDelegate!

    private var streamRef: FSEventStreamRef!
    public var started: Bool = false
    
    init(paths: [String], latency: CFTimeInterval) {
        var context = FSEventStreamContext()
        context.info = unsafeBitCast(self, to: UnsafeMutableRawPointer.self)
        streamRef = FSEventStreamCreate(
            kCFAllocatorDefault,
            { _, contextInfo, _, eventPaths, _, _ in
                let paths = unsafeBitCast(eventPaths, to: NSArray.self) as! [String]
                let obj = unsafeBitCast(contextInfo, to: DirectoryMonitor.self)
                obj.pathsChanged(paths)
        },
            &context,
            paths as CFArray,
            UInt64(kFSEventStreamEventIdSinceNow),
            latency,
            UInt32(kFSEventStreamCreateFlagFileEvents | kFSEventStreamCreateFlagUseCFTypes)
        )
        
        if streamRef == nil {
            fatalError("Cannot create streamRef")
        }
	}
    
    public func start() {
        FSEventStreamScheduleWithRunLoop(streamRef, CFRunLoopGetMain(), CFRunLoopMode.defaultMode.rawValue)
        FSEventStreamStart(streamRef)
        started = true
    }
    
    public func stop() {
        guard started == true else {
            return
        }
        
        FSEventStreamStop(streamRef)
        FSEventStreamInvalidate(streamRef)
        FSEventStreamRelease(streamRef)
        
        streamRef = nil
        started = false
    }

	private func pathsChanged(_ paths: [String]) {
		delegate?.pathsDidChange(paths)
	}

    deinit {
        FSEventStreamStop(streamRef)
        FSEventStreamInvalidate(streamRef)
        FSEventStreamRelease(streamRef)
    }
}
