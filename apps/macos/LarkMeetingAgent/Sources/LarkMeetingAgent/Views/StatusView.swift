import LarkMeetingAgentCore
import SwiftUI

struct StatusView: View {
    @ObservedObject var viewModel: StatusViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Lark Meeting Agent")
                .font(.headline)
            Text(statusText)
            Text("Pending approvals: \(viewModel.pendingApprovalCount)")
            Button("Refresh") {
                Task {
                    await viewModel.refreshStatus()
                }
            }
            Divider()
            Button("Settings...") {
                NSApp.sendAction(Selector(("showSettingsWindow:")), to: nil, from: nil)
            }
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
        }
        .padding()
        .frame(width: 280)
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
