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
        VStack(alignment: .leading, spacing: 22) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Upload")
                    .font(.system(size: 22, weight: .semibold))
                Text("Create a dry-run write plan from a local text transcript.")
                    .font(.system(size: 14))
                    .foregroundStyle(.secondary)
            }
            VStack(alignment: .leading, spacing: 12) {
                Toggle("Create doc preview", isOn: $createDoc)
                Toggle("Create task previews", isOn: $createTasks)
                Toggle("Prepare IM preview", isOn: $sendMessage)
            }
            TextField("Chat ID", text: $chatID)
                .textFieldStyle(.roundedBorder)
                .disabled(!sendMessage)
            Button {
                importerPresented = true
            } label: {
                Label("Choose .txt/.md/.json", systemImage: "square.and.arrow.up")
            }
            .buttonStyle(.borderedProminent)
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
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                        Text("Run \(upload.runID)")
                            .font(.system(size: 14, weight: .medium))
                    }
                    Text(upload.status)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    ForEach(upload.errors, id: \.self) { error in
                        Text("Error: \(error)")
                            .font(.caption)
                            .foregroundStyle(.red)
                    }
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(Color(nsColor: .textBackgroundColor))
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .strokeBorder(Color(nsColor: .separatorColor).opacity(0.45), lineWidth: 1)
                )
            }
        }
    }
}
