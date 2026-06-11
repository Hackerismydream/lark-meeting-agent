import Foundation

@MainActor
public final class SearchUploadViewModel: ObservableObject {
    @Published public private(set) var answer: QAAnswer?
    @Published public private(set) var uploadResult: UploadTranscriptResult?
    @Published public private(set) var isLoading = false
    @Published public private(set) var message: String?

    private let makeClient: () -> AgentAPIClient

    public init(settingsStore: AppSettingsStore = AppSettingsStore(), credentialStore: CredentialStore = KeychainCredentialStore()) {
        self.makeClient = {
            let settings = settingsStore.load()
            return AgentAPIClient(baseURL: settings.apiBaseURL) {
                try? credentialStore.loadToken()
            }
        }
    }

    public init(makeClient: @escaping () -> AgentAPIClient) {
        self.makeClient = makeClient
    }

    public func search(question: String) async {
        guard !question.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            message = "Enter a question before searching."
            return
        }
        isLoading = true
        message = nil
        do {
            answer = try await makeClient().search(question: question)
        } catch {
            message = "Search failed."
        }
        isLoading = false
    }

    public func uploadTranscriptFile(url: URL, createDoc: Bool, createTasks: Bool, sendMessage: Bool, chatID: String?) async {
        guard Self.allowedTranscriptExtensions.contains(url.pathExtension.lowercased()) else {
            message = "Only .txt, .md, and .json transcript files are supported."
            return
        }
        isLoading = true
        message = nil
        let canAccess = url.startAccessingSecurityScopedResource()
        defer {
            if canAccess {
                url.stopAccessingSecurityScopedResource()
            }
        }
        do {
            let content = try String(contentsOf: url, encoding: .utf8)
            uploadResult = try await makeClient().uploadTranscript(
                filename: url.lastPathComponent,
                content: content,
                createDoc: createDoc,
                createTasks: createTasks,
                sendMessage: sendMessage,
                chatID: chatID?.isEmpty == true ? nil : chatID
            )
            NotificationCenter.default.post(name: .larkMeetingAgentRunsChanged, object: nil)
        } catch {
            message = "Transcript upload failed."
        }
        isLoading = false
    }

    nonisolated public static let allowedTranscriptExtensions: Set<String> = ["txt", "md", "json"]
}
