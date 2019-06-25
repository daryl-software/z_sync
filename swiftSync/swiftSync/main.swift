//
//  main.swift
//  swiftSync
//
//  Created by Florian Morello on 11/06/2019.
//  Copyright © 2019 Florian Morello. All rights reserved.
//

import Foundation

let pwd = Process().currentDirectoryPath
guard let data = try? Data(contentsOf: URL(fileURLWithPath: "\(pwd)/swiftsync.json")), let config = try? JSONDecoder().decode(App.Config.self, from: data) else {
    fatalError("Error: Couldn't open/decode swiftsync.json")
}

let app = App(config: config)
app.start()

RunLoop.main.run()

