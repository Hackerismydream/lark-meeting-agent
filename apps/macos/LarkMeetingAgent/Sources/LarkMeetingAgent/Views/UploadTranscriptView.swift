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
                Text("从这里开始")
                    .font(.system(size: 22, weight: .semibold))
                Text("导入会议转写，先预览生成的写入计划，再决定是否写回飞书。")
                    .font(.system(size: 14))
                    .foregroundStyle(.secondary)
            }
            workflowGuide
            VStack(alignment: .leading, spacing: 12) {
                Toggle("生成文档预览", isOn: $createDoc)
                Toggle("生成任务预览", isOn: $createTasks)
                Toggle("生成群消息预览", isOn: $sendMessage)
            }
            TextField("群聊 ID", text: $chatID)
                .textFieldStyle(.roundedBorder)
                .disabled(!sendMessage)
            Button {
                importerPresented = true
            } label: {
                Label("选择 .txt/.md/.json", systemImage: "square.and.arrow.up")
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
                        Text("运行 \(upload.runID)")
                            .font(.system(size: 14, weight: .medium))
                    }
                    Text(upload.status.localizedUploadStatus)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    ForEach(upload.errors, id: \.self) { error in
                        Text("错误：\(error)")
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

    private var workflowGuide: some View {
        VStack(alignment: .leading, spacing: 10) {
            WorkflowStep(number: "1", title: "选择会议转写", detail: "支持 .txt、.md 或 .json 会议转写。本版本不处理音频。")
            WorkflowStep(number: "2", title: "审批写入计划", detail: "系统只生成 dry-run 预览；你审批前不会写入飞书。")
            WorkflowStep(number: "3", title: "搜索或准备下一场会议", detail: "上传后可用搜索做带来源的问答，也可用会前简报准备下一场会议。")
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

private extension String {
    var localizedUploadStatus: String {
        switch self {
        case "completed":
            return "已完成"
        case "approval_required":
            return "待审批"
        case "failed":
            return "失败"
        case "running":
            return "运行中"
        default:
            return self
        }
    }
}

private struct WorkflowStep: View {
    let number: String
    let title: String
    let detail: String

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Text(number)
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(.white)
                .frame(width: 20, height: 20)
                .background(Circle().fill(Color.blue))
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 13, weight: .semibold))
                Text(detail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
