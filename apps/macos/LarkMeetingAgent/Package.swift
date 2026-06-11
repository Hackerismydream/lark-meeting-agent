// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "LarkMeetingAgent",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "LarkMeetingAgent", targets: ["LarkMeetingAgent"]),
        .library(name: "LarkMeetingAgentCore", targets: ["LarkMeetingAgentCore"]),
    ],
    targets: [
        .target(name: "LarkMeetingAgentCore"),
        .executableTarget(
            name: "LarkMeetingAgent",
            dependencies: ["LarkMeetingAgentCore"]
        ),
        .executableTarget(
            name: "LarkMeetingAgentCoreSmokeTests",
            dependencies: ["LarkMeetingAgentCore"]
        ),
    ]
)
