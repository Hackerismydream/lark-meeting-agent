import LarkMeetingAgentCore
import SwiftUI
import UniformTypeIdentifiers

struct UploadTranscriptView: View {
    @ObservedObject var viewModel: SearchUploadViewModel
    @State private var importerPresented = false
    @State private var createDoc = true
    @State private var createTasks = true
    @State private var sendMessage = false
    @State private var chatID = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Upload transcript")
                .font(.headline)
            Toggle("Create doc preview", isOn: $createDoc)
            Toggle("Create task previews", isOn: $createTasks)
            Toggle("Prepare IM preview", isOn: $sendMessage)
            TextField("Chat ID", text: $chatID)
                .disabled(!sendMessage)
            Button("Choose .txt/.md/.json") {
                importerPresented = true
            }
            .fileImporter(
                isPresented: $importerPresented,
                allowedContentTypes: [.plainText, .json],
                allowsMultipleSelection: false
            ) { result in
                if case .success(let urls) = result, let url = urls.first {
                    Task {
                        await viewModel.uploadTranscriptFile(
                            url: url,
                            createDoc: createDoc,
                            createTasks: createTasks,
                            sendMessage: sendMessage,
                            chatID: chatID
                        )
                    }
                }
            }
            if let upload = viewModel.uploadResult {
                Text("Run \(upload.runID): \(upload.status)")
                    .font(.caption)
                ForEach(upload.errors, id: \.self) { error in
                    Text("Error: \(error)")
                        .font(.caption)
                        .foregroundStyle(.red)
                }
            }
        }
    }
}
