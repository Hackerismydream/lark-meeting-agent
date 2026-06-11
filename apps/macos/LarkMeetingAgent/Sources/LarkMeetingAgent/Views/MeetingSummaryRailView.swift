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
            Text("会议")
                .font(.system(size: 15, weight: .semibold))
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: "person.2.fill")
                    .font(.title3)
                    .foregroundStyle(.blue)
                    .frame(width: 26)
                VStack(alignment: .leading, spacing: 4) {
                    Text("本地会议工作台")
                        .font(.system(size: 14, weight: .medium))
                    Text("本地开发环境")
                        .font(.system(size: 12))
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var summaryBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("概览")
                .font(.system(size: 15, weight: .semibold))
            RailMetric(icon: "doc.text", label: "来源", value: "证据")
            RailMetric(icon: "checklist", label: "待审批", value: "\(pendingApprovalCount)")
            RailMetric(icon: "rectangle.3.group", label: "当前页", value: selectedSection)
        }
    }

    private var runBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("运行")
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
            Text("存储")
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
                Label("设置...", systemImage: "gearshape")
            }
            .buttonStyle(.bordered)

            Button("退出") {
                NSApplication.shared.terminate(nil)
            }
            .buttonStyle(.bordered)
        }
    }

    private var repositoryText: String {
        if case .connected(let status) = connectionState {
            return "\(status.providerMode) / \(status.storage)"
        }
        return "未连接"
    }

    private var statusLabel: String {
        switch connectionState {
        case .connected:
            return "已连接"
        case .connecting:
            return "连接中"
        case .failed:
            return "不可用"
        case .disconnected:
            return "未连接"
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
        pendingApprovalCount == 0 ? "就绪" : "需要审批"
    }

    private var runSubtitle: String {
        pendingApprovalCount == 0 ? "没有待写入操作" : "\(pendingApprovalCount) 个待审批操作"
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
