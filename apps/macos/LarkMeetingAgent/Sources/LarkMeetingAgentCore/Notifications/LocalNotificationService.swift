import Foundation
@preconcurrency import UserNotifications

public protocol NotificationScheduling: Sendable {
    func notifyPendingApprovals(count: Int) async
    func notifyPreBriefAvailable(title: String) async
}

public struct LocalNotificationService: NotificationScheduling, @unchecked Sendable {
    private let center: UNUserNotificationCenter

    public init(center: UNUserNotificationCenter = .current()) {
        self.center = center
    }

    public func notifyPendingApprovals(count: Int) async {
        guard count > 0, await authorizationAvailable() else {
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
        guard await authorizationAvailable() else {
            return
        }
        let content = UNMutableNotificationContent()
        content.title = "Pre-brief ready"
        content.body = title
        content.sound = .default
        let request = UNNotificationRequest(identifier: "prebrief-ready-\(UUID().uuidString)", content: content, trigger: nil)
        try? await center.add(request)
    }

    private func authorizationAvailable() async -> Bool {
        let settings = await center.notificationSettings()
        if settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional {
            return true
        }
        return (try? await center.requestAuthorization(options: [.alert, .sound])) == true
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
