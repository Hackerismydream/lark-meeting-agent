import Foundation

@MainActor
public final class PreBriefTraceViewModel: ObservableObject {
    @Published public private(set) var meetings: [MeetingSummary] = []
    @Published public private(set) var meetingsSource: String?
    @Published public private(set) var preBrief: PreBrief?
    @Published public private(set) var runs: [RunDetail] = []
    @Published public private(set) var selectedRun: RunDetail?
    @Published public private(set) var trace: RunTrace?
    @Published public private(set) var isLoading = false
    @Published public private(set) var message: String?

    private let makeClient: () -> AgentAPIClient
    private let notificationService: NotificationScheduling
    private let settingsStore: AppSettingsStore

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
        self.settingsStore = AppSettingsStore(defaults: UserDefaults(suiteName: "PreBriefTraceViewModelTests") ?? .standard)
        self.makeClient = makeClient
        self.notificationService = notificationService
    }

    public func refreshMeetingsAndRuns() async {
        isLoading = true
        message = nil
        do {
            let response = try await makeClient().meetingsToday()
            meetings = response.items
            meetingsSource = response.source
            runs = try await makeClient().runs()
        } catch {
            message = "Unable to load meetings or runs."
        }
        isLoading = false
    }

    public func generatePreBrief(query: String, meetingID: String?, meetingType: String, project: String?, customer: String?) async {
        isLoading = true
        message = nil
        do {
            let brief = try await makeClient().preBrief(
                query: query.isEmpty ? nil : query,
                meetingID: meetingID?.isEmpty == true ? nil : meetingID,
                meetingType: meetingType.isEmpty ? "general" : meetingType,
                project: project?.isEmpty == true ? nil : project,
                customer: customer?.isEmpty == true ? nil : customer
            )
            preBrief = brief
            if settingsStore.load().notificationsEnabled {
                await notificationService.notifyPreBriefAvailable(title: brief.goal)
            }
        } catch {
            message = "Unable to generate pre-brief."
        }
        isLoading = false
    }

    public func inspectRun(_ runID: String) async {
        isLoading = true
        message = nil
        do {
            selectedRun = try await makeClient().run(runID: runID)
            trace = try await makeClient().trace(runID: runID)
        } catch {
            message = "Unable to load run trace."
        }
        isLoading = false
    }
}
