import Foundation

@MainActor
public final class StatusViewModel: ObservableObject {
    @Published public private(set) var connectionState: ConnectionState = .disconnected
    @Published public private(set) var pendingApprovalCount: Int = 0
    @Published public var settings: AppSettings

    private let settingsStore: AppSettingsStore
    private let credentialStore: CredentialStore
    private var makeClient: (URL, @escaping @Sendable () -> String?) -> AgentAPIClient

    public init(
        settingsStore: AppSettingsStore = AppSettingsStore(),
        credentialStore: CredentialStore = KeychainCredentialStore(),
        makeClient: @escaping (URL, @escaping @Sendable () -> String?) -> AgentAPIClient
    ) {
        self.settingsStore = settingsStore
        self.credentialStore = credentialStore
        self.settings = settingsStore.load()
        self.makeClient = makeClient
    }

    public convenience init() {
        self.init { baseURL, tokenProvider in
            AgentAPIClient(baseURL: baseURL, bearerTokenProvider: tokenProvider)
        }
    }

    public func refreshStatus() async {
        connectionState = .connecting
        let client = makeClient(settings.apiBaseURL) { [credentialStore] in
            try? credentialStore.loadToken()
        }
        do {
            let status = try await client.status()
            let plans = try await client.pendingWritePlans()
            pendingApprovalCount = plans.reduce(0) { total, plan in
                total + plan.operations.filter { $0.approvalStatus == "pending" }.count
            }
            connectionState = .connected(status)
        } catch {
            pendingApprovalCount = 0
            connectionState = .failed("无法连接 Agent 服务")
        }
    }

    public func saveSettings(apiBaseURL: URL, environmentLabel: String, notificationsEnabled: Bool) {
        settings = AppSettings(apiBaseURL: apiBaseURL, environmentLabel: environmentLabel, notificationsEnabled: notificationsEnabled)
        settingsStore.save(settings)
    }
}
