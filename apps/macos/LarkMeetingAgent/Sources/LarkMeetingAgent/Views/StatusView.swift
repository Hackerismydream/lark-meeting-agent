import LarkMeetingAgentCore
import SwiftUI

struct StatusView: View {
    @ObservedObject var viewModel: StatusViewModel
    @State private var settingsPresented = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            header
            Divider()
            TabView {
                ScrollView {
                    ApprovalInboxView()
                        .padding()
                }
                .tabItem {
                    Text("Approvals")
                }

                ScrollView {
                    PreBriefTracePanelView()
                        .padding()
                }
                .tabItem {
                    Text("Pre-brief")
                }

                ScrollView {
                    SearchUploadPanelView()
                        .padding()
                }
                .tabItem {
                    Text("Search & Upload")
                }
            }
            HStack {
                Button("Settings...") {
                    settingsPresented = true
                }
                Button("Quit") {
                    NSApplication.shared.terminate(nil)
                }
            }
        }
        .padding()
        .frame(minWidth: 520, minHeight: 640)
        .task {
            await viewModel.refreshStatus()
        }
        .sheet(isPresented: $settingsPresented) {
            SettingsView(viewModel: viewModel)
        }
        .onReceive(NotificationCenter.default.publisher(for: .larkMeetingAgentRunsChanged)) { _ in
            Task {
                await viewModel.refreshStatus()
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Lark Meeting Agent")
                .font(.headline)
            Text(statusText)
            Text("Pending approvals: \(viewModel.pendingApprovalCount)")
            Button("Refresh") {
                Task {
                    await viewModel.refreshStatus()
                }
            }
        }
    }

    private var statusText: String {
        switch viewModel.connectionState {
        case .disconnected:
            return "Disconnected"
        case .connecting:
            return "Connecting..."
        case .connected(let status):
            return "Connected: \(status.environmentSummary)"
        case .failed:
            return "Disconnected"
        }
    }
}

private extension AgentStatus {
    var environmentSummary: String {
        "\(providerMode) / \(storage)"
    }
}
