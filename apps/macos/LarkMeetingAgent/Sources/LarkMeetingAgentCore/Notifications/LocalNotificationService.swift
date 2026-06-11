import Foundation
@preconcurrency import UserNotifications

public protocol NotificationScheduling: Sendable {
    func notifyPendingApprovals(count: Int) async
    func notifyPreBriefAvailable(title: String) async
}

public struct LocalNotificationService: NotificationScheduling, @unchecked Sendable {
    private let centerProvider: @Sendable () -> UNUserNotificationCenter?

    public init(centerProvider: @escaping @Sendable () -> UNUserNotificationCenter? = Self.defaultCenter) {
        self.centerProvider = centerProvider
    }

    public init(center: UNUserNotificationCenter) {
        self.centerProvider = { center }
    }

    public func notifyPendingApprovals(count: Int) async {
        guard count > 0, let center = centerProvider(), await authorizationAvailable(center) else {
            return
        }
        let content = UNMutableNotificationContent()
        content.title = "Lark Meeting Agent"
        content.body = "\(count) pending approval item(s) need review."
        content.sound = .default
        let request = UNNotificationRequest(identifier: "pending-approvals", content: content, trigger: nil)
        try? await center.add(request)
    }

    public func notifyPreBriefAvailable(title: String) async {
        guard let center = centerProvider(), await authorizationAvailable(center) else {
            return
        }
        let content = UNMutableNotificationContent()
        content.title = "Pre-brief ready"
        content.body = title
        content.sound = .default
        let request = UNNotificationRequest(identifier: "prebrief-ready-\(UUID().uuidString)", content: content, trigger: nil)
        try? await center.add(request)
    }

    private func authorizationAvailable(_ center: UNUserNotificationCenter) async -> Bool {
        let settings = await center.notificationSettings()
        if settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional {
            return true
        }
        return (try? await center.requestAuthorization(options: [.alert, .sound])) == true
    }

    public static func defaultCenter() -> UNUserNotificationCenter? {
        if Bundle.main.bundleIdentifier == nil {
            return nil
        }
        return UNUserNotificationCenter.current()
    }
}

public struct NoopNotificationService: NotificationScheduling {
    public init() {}

    public func notifyPendingApprovals(count: Int) async {
        _ = count
    }

    public func notifyPreBriefAvailable(title: String) async {
        _ = title
    }
}
