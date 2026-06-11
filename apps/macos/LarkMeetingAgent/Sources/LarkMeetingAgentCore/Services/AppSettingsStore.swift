import Foundation

public struct AppSettings: Equatable, Sendable {
    public var apiBaseURL: URL
    public var environmentLabel: String
    public var notificationsEnabled: Bool

    public init(
        apiBaseURL: URL = URL(string: "http://127.0.0.1:8765")!,
        environmentLabel: String = "本地",
        notificationsEnabled: Bool = true
    ) {
        self.apiBaseURL = apiBaseURL
        self.environmentLabel = environmentLabel
        self.notificationsEnabled = notificationsEnabled
    }
}

public final class AppSettingsStore {
    private let defaults: UserDefaults

    public init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    public func load() -> AppSettings {
        let urlString = defaults.string(forKey: "apiBaseURL") ?? "http://127.0.0.1:8765"
        return AppSettings(
            apiBaseURL: URL(string: urlString) ?? URL(string: "http://127.0.0.1:8765")!,
            environmentLabel: defaults.string(forKey: "environmentLabel") ?? "本地",
            notificationsEnabled: defaults.object(forKey: "notificationsEnabled") as? Bool ?? true
        )
    }

    public func save(_ settings: AppSettings) {
        defaults.set(settings.apiBaseURL.absoluteString, forKey: "apiBaseURL")
        defaults.set(settings.environmentLabel, forKey: "environmentLabel")
        defaults.set(settings.notificationsEnabled, forKey: "notificationsEnabled")
    }
}
