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
                Text("Use existing meeting memory to prepare context before the next meeting. Upload transcripts first if memory is empty.")
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
            labeledTextField("Meeting query", placeholder: "project review, customer name, or topic", text: $query)
            HStack(spacing: 10) {
                labeledTextField("Meeting ID", placeholder: "optional", text: $meetingID)
                labeledTextField("Meeting type", placeholder: "general", text: $meetingType)
            }
            HStack(spacing: 10) {
                labeledTextField("Project", placeholder: "optional", text: $project)
                labeledTextField("Customer", placeholder: "optional", text: $customer)
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
