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
            message = "请输入问题后再搜索。"
            return
        }
        isLoading = true
        message = nil
        do {
            answer = try await makeClient().search(question: question)
        } catch {
            message = "搜索失败。"
        }
        isLoading = false
    }

    public func uploadTranscriptFile(url: URL, createDoc: Bool, createTasks: Bool, sendMessage: Bool, chatID: String?) async {
        guard Self.allowedTranscriptExtensions.contains(url.pathExtension.lowercased()) else {
            message = "仅支持 .txt、.md 和 .json 会议转写文件。"
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
            message = "会议转写上传失败。"
        }
        isLoading = false
    }

    nonisolated public static let allowedTranscriptExtensions: Set<String> = ["txt", "md", "json"]
}
