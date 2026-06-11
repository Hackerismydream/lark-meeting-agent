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
                Text("Pre-brief")
                    .font(.system(size: 22, weight: .semibold))
                Text("Prepare context, open questions, and source-backed reminders before a meeting.")
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
            Button("Refresh meetings and runs") {
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
            labeledTextField("Meeting query", text: $query)
            HStack(spacing: 10) {
                labeledTextField("Meeting ID", text: $meetingID)
                labeledTextField("Meeting type", text: $meetingType)
            }
            HStack(spacing: 10) {
                labeledTextField("Project", text: $project)
                labeledTextField("Customer", text: $customer)
            }
            Button {
                generatePreBrief()
            } label: {
                Label("Generate pre-brief", systemImage: "sparkles")
            }
            .buttonStyle(.borderedProminent)
            .padding(.top, 4)
        }
    }

    private func labeledTextField(_ label: String, text: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
            TextField(label, text: text)
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
