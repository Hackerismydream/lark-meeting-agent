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
            VStack(alignment: .leading, spacing: 6) {
                TextField("Meeting query", text: $query)
                TextField("Meeting ID", text: $meetingID)
                TextField("Meeting type", text: $meetingType)
                TextField("Project", text: $project)
                TextField("Customer", text: $customer)
                Button("Generate pre-brief") {
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
    }
}
