import LarkMeetingAgentCore
import SwiftUI

struct PreBriefTracePanelView: View {
    @StateObject private var viewModel = PreBriefTraceViewModel()
    @State private var query = ""
    @State private var meetingID = ""
    @State private var meetingType = "general"
    @State private var project = ""
    @State private var customer = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            VStack(alignment: .leading, spacing: 8) {
                Text("会前简报")
                    .font(.system(size: 22, weight: .semibold))
                Text("基于已有会议记忆，为下一场会议准备背景、风险和建议追问。记忆为空时请先上传会议转写。")
                    .font(.system(size: 14))
                    .foregroundStyle(.secondary)
            }
            MeetingsView(meetings: viewModel.meetings, source: viewModel.meetingsSource)
            preBriefForm
            PreBriefView(preBrief: viewModel.preBrief)
            RunTraceView(
                runs: viewModel.runs,
                selectedRun: viewModel.selectedRun,
                trace: viewModel.trace,
                inspectRun: { runID in
                    Task {
                        await viewModel.inspectRun(runID)
                    }
                }
            )
            if viewModel.isLoading {
                ProgressView()
            }
            if let message = viewModel.message {
                Text(message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Button("刷新会议和运行记录") {
                Task {
                    await viewModel.refreshMeetingsAndRuns()
                }
            }
        }
        .task {
            await viewModel.refreshMeetingsAndRuns()
        }
        .onReceive(NotificationCenter.default.publisher(for: .larkMeetingAgentRunsChanged)) { _ in
            Task {
                await viewModel.refreshMeetingsAndRuns()
            }
        }
    }

    private var preBriefForm: some View {
        VStack(alignment: .leading, spacing: 6) {
            labeledTextField("会议查询", placeholder: "项目评审、客户名称或讨论主题", text: $query)
            HStack(spacing: 10) {
                labeledTextField("会议 ID", placeholder: "可选", text: $meetingID)
                labeledTextField("会议类型", placeholder: "通用", text: $meetingType)
            }
            HStack(spacing: 10) {
                labeledTextField("项目", placeholder: "可选", text: $project)
                labeledTextField("客户", placeholder: "可选", text: $customer)
            }
            Button {
                generatePreBrief()
            } label: {
                Label("生成会前简报", systemImage: "sparkles")
            }
            .buttonStyle(.borderedProminent)
            .padding(.top, 4)
        }
    }

    private func labeledTextField(_ label: String, placeholder: String, text: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
            TextField(placeholder, text: text)
                .textFieldStyle(.roundedBorder)
                .onSubmit {
                    generatePreBrief()
                }
        }
    }

    private func generatePreBrief() {
        Task {
            await viewModel.generatePreBrief(
                query: query,
                meetingID: meetingID,
                meetingType: meetingType,
                project: project,
                customer: customer
            )
        }
    }
}
