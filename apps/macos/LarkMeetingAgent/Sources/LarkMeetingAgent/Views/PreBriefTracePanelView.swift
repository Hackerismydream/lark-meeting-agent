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
        VStack(alignment: .leading, spacing: 10) {
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
            labeledTextField("Meeting ID", text: $meetingID)
            labeledTextField("Meeting type", text: $meetingType)
            labeledTextField("Project", text: $project)
            labeledTextField("Customer", text: $customer)
            Button("Generate pre-brief") {
                generatePreBrief()
            }
        }
    }

    private func labeledTextField(_ label: String, text: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
            TextField(label, text: text)
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
