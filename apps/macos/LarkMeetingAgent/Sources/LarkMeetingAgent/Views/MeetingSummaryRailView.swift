import LarkMeetingAgentCore
import SwiftUI

struct MeetingSummaryRailView: View {
    let connectionState: ConnectionState
    let pendingApprovalCount: Int
    let selectedSection: String
    @Binding var settingsPresented: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            meetingBlock
            Divider()
            summaryBlock
            Divider()
            runBlock
            Divider()
            repositoryBlock
            Spacer()
            footerActions
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 28)
        .frame(width: 270)
        .frame(maxHeight: .infinity, alignment: .top)
        .background(Color(nsColor: .controlBackgroundColor).opacity(0.54))
    }

    private var meetingBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Meeting")
                .font(.system(size: 15, weight: .semibold))
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: "person.2.fill")
                    .font(.title3)
                    .foregroundStyle(.blue)
                    .frame(width: 26)
                VStack(alignment: .leading, spacing: 4) {
                    Text("macOS companion sync")
                        .font(.system(size: 14, weight: .medium))
                    Text("Local development")
                        .font(.system(size: 12))
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var summaryBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Summary")
                .font(.system(size: 15, weight: .semibold))
            RailMetric(icon: "doc.text", label: "Sources", value: "Evidence")
            RailMetric(icon: "checklist", label: "Pending", value: "\(pendingApprovalCount)")
            RailMetric(icon: "rectangle.3.group", label: "View", value: selectedSection)
        }
    }

    private var runBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Run")
                .font(.system(size: 15, weight: .semibold))
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: runIcon)
                    .foregroundStyle(runColor)
                    .font(.title3)
                    .frame(width: 26)
                VStack(alignment: .leading, spacing: 4) {
                    Text(runTitle)
                        .font(.system(size: 14, weight: .medium))
                    Text(runSubtitle)
                        .font(.system(size: 12))
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var repositoryBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Repository")
                .font(.system(size: 15, weight: .semibold))
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: "externaldrive")
                    .font(.title3)
                    .frame(width: 26)
                VStack(alignment: .leading, spacing: 4) {
                    Text(repositoryText)
                        .font(.system(size: 13, weight: .medium))
                        .lineLimit(2)
                    HStack(spacing: 6) {
                        Circle()
                            .fill(statusColor)
                            .frame(width: 8, height: 8)
                        Text(statusLabel)
                            .font(.system(size: 12))
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
    }

    private var footerActions: some View {
        HStack(spacing: 10) {
            Button {
                settingsPresented = true
            } label: {
                Label("Settings...", systemImage: "gearshape")
            }
            .buttonStyle(.bordered)

            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
            .buttonStyle(.bordered)
        }
    }

    private var repositoryText: String {
        if case .connected(let status) = connectionState {
            return "\(status.providerMode) / \(status.storage)"
        }
        return "Not connected"
    }

    private var statusLabel: String {
        switch connectionState {
        case .connected:
            return "Connected"
        case .connecting:
            return "Connecting"
        case .failed:
            return "Unavailable"
        case .disconnected:
            return "Disconnected"
        }
    }

    private var statusColor: Color {
        switch connectionState {
        case .connected:
            return .green
        case .connecting:
            return .orange
        case .failed, .disconnected:
            return .red
        }
    }

    private var runIcon: String {
        pendingApprovalCount == 0 ? "checkmark.circle.fill" : "exclamationmark.circle.fill"
    }

    private var runColor: Color {
        pendingApprovalCount == 0 ? .green : .orange
    }

    private var runTitle: String {
        pendingApprovalCount == 0 ? "Ready" : "Approval required"
    }

    private var runSubtitle: String {
        pendingApprovalCount == 0 ? "No pending writes" : "\(pendingApprovalCount) operation(s)"
    }
}

private struct RailMetric: View {
    let icon: String
    let label: String
    let value: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundStyle(.secondary)
                .frame(width: 24)
            Text(label)
                .font(.system(size: 13))
            Spacer()
            Text(value)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(.secondary)
        }
    }
}

struct StatusPill: View {
    let text: String
    let color: Color

    var body: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(color)
                .frame(width: 7, height: 7)
            Text(text)
                .font(.system(size: 12))
                .foregroundStyle(.secondary)
                .lineLimit(1)
        }
        .padding(.horizontal, 9)
        .padding(.vertical, 5)
        .background(
            Capsule()
                .fill(Color(nsColor: .controlBackgroundColor))
        )
    }
}
