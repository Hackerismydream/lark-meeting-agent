import Foundation

@MainActor
public final class ApprovalInboxViewModel: ObservableObject {
    @Published public private(set) var plans: [PendingWritePlan] = []
    @Published public private(set) var isLoading = false
    @Published public private(set) var message: String?
    @Published public var selectedOperationIDs: Set<String> = []

    private let settingsStore: AppSettingsStore
    private let makeClient: () -> AgentAPIClient
    private let notificationService: NotificationScheduling

    public init(
        settingsStore: AppSettingsStore = AppSettingsStore(),
        credentialStore: CredentialStore = KeychainCredentialStore(),
        notificationService: NotificationScheduling = LocalNotificationService()
    ) {
        self.settingsStore = settingsStore
        self.notificationService = notificationService
        self.makeClient = {
            let settings = settingsStore.load()
            return AgentAPIClient(baseURL: settings.apiBaseURL) {
                try? credentialStore.loadToken()
            }
        }
    }

    public init(makeClient: @escaping () -> AgentAPIClient, notificationService: NotificationScheduling = NoopNotificationService()) {
        self.settingsStore = AppSettingsStore(defaults: UserDefaults(suiteName: "ApprovalInboxViewModelTests") ?? .standard)
        self.makeClient = makeClient
        self.notificationService = notificationService
    }

    public var pendingOperationCount: Int {
        plans.reduce(0) { total, plan in
            total + plan.operations.filter { $0.approvalStatus == "pending" }.count
        }
    }

    public func refresh() async {
        isLoading = true
        message = nil
        do {
            let loadedPlans = try await makeClient().pendingWritePlans()
            plans = loadedPlans
            selectedOperationIDs.formIntersection(Set(loadedPlans.flatMap { plan in plan.operations.map { Self.selectionKey(runID: plan.runID, operationID: $0.operationID) } }))
            if settingsStore.load().notificationsEnabled {
                await notificationService.notifyPendingApprovals(count: pendingOperationCount)
            }
        } catch {
            message = "无法加载待审批项。"
        }
        isLoading = false
    }

    public func toggleSelection(runID: String, operationID: String, isSelected: Bool) {
        let key = Self.selectionKey(runID: runID, operationID: operationID)
        if isSelected {
            selectedOperationIDs.insert(key)
        } else {
            selectedOperationIDs.remove(key)
        }
    }

    public func approveSelected(runID: String) async {
        let operationIDs = selectedOperationIDsForRun(runID)
        guard !operationIDs.isEmpty else {
            message = "请至少选择一个操作后再批准。"
            return
        }
        isLoading = true
        do {
            try await makeClient().approve(runID: runID, operationIDs: operationIDs)
            selectedOperationIDs.subtract(operationIDs.map { Self.selectionKey(runID: runID, operationID: $0) })
            message = "已批准 \(operationIDs.count) 个操作。"
            await refresh()
            NotificationCenter.default.post(name: .larkMeetingAgentRunsChanged, object: nil)
        } catch {
            message = "批准失败。"
        }
        isLoading = false
    }

    public func approveOperation(runID: String, operationID: String) async {
        isLoading = true
        do {
            try await makeClient().approve(runID: runID, operationIDs: [operationID])
            selectedOperationIDs.remove(Self.selectionKey(runID: runID, operationID: operationID))
            message = "已批准 \(operationID)。"
            await refresh()
            NotificationCenter.default.post(name: .larkMeetingAgentRunsChanged, object: nil)
        } catch {
            message = "批准失败。"
        }
        isLoading = false
    }

    public func reject(runID: String) async {
        isLoading = true
        do {
            try await makeClient().reject(runID: runID, reason: "从 macOS companion app 拒绝")
            selectedOperationIDs.subtract(selectedOperationIDsForRun(runID).map { Self.selectionKey(runID: runID, operationID: $0) })
            message = "已拒绝运行 \(runID)。"
            await refresh()
            NotificationCenter.default.post(name: .larkMeetingAgentRunsChanged, object: nil)
        } catch {
            message = "拒绝失败。"
        }
        isLoading = false
    }

    public func selectedOperationIDsForRun(_ runID: String) -> [String] {
        guard let plan = plans.first(where: { $0.runID == runID }) else {
            return []
        }
        return plan.operations
            .map(\.operationID)
            .filter { selectedOperationIDs.contains(Self.selectionKey(runID: runID, operationID: $0)) }
            .sorted()
    }

    public func isSelected(runID: String, operationID: String) -> Bool {
        selectedOperationIDs.contains(Self.selectionKey(runID: runID, operationID: operationID))
    }

    private static func selectionKey(runID: String, operationID: String) -> String {
        "\(runID)::\(operationID)"
    }
}
