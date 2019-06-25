//
//  Extensions.swift
//  swiftSync
//
//  Created by Florian Morello on 25/06/2019.
//  Copyright © 2019 Florian Morello. All rights reserved.
//

import Foundation

extension String {
    func trimmed() -> String {
        return trimmingCharacters(in: CharacterSet(charactersIn: "\n\r"))
    }
}
