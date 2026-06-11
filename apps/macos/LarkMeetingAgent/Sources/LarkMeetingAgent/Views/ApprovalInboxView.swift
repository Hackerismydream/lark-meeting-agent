import LarkMeetingAgentCore
import SwiftUI

struct ApprovalInboxView: View {
    @StateObject private var viewModel = ApprovalInboxViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            header
            Divider()
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, minHeight: 220)
            } else if viewModel.plans.isEmpty {
                emptyState
            } else {
                VStack(spacing: 0) {
                    ForEach(viewModel.plans) { plan in
                        planView(plan)
                        Divider()
                    }
                }
            }
            if let message = viewModel.message {
                Text(message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .task {
            await viewModel.refresh()
        }
        .onReceive(NotificationCenter.default.publisher(for: .larkMeetingAgentRunsChanged)) { _ in
            Task {
                await viewModel.refresh()
            }
        }
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 10) {
                    Text("Approvals")
                        .font(.system(size: 22, weight: .semibold))
                    if viewModel.pendingOperationCount > 0 {
                        Text("Pending")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundStyle(.orange)
                            .padding(.horizontal, 9)
                            .padding(.vertical, 4)
                            .background(
                                Capsule()
                                    .fill(Color.orange.opacity(0.12))
                            )
                        Text("\(viewModel.pendingOperationCount)")
                            .foregroundStyle(.secondary)
                    }
                }
                Text("Review and approve or reject pending operations.")
                    .font(.system(size: 14))
                    .foregroundStyle(.secondary)
            }
            Spacer()
            Button {
                Task {
                    await viewModel.refresh()
                }
            } label: {
                Label("Refresh", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.bordered)
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 38))
                .foregroundStyle(.green)
            Text("No pending approvals")
                .font(.system(size: 15, weight: .medium))
            Text("Approved write plans and rejected runs will disappear from this inbox.")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, minHeight: 260)
    }

    private func planView(_ plan: PendingWritePlan) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(plan.operations) { operation in
                ApprovalOperationRow(
                    runID: plan.runID,
                    operation: operation,
                    approve: {
                        Task {
                            await viewModel.approveOperation(runID: plan.runID, operationID: operation.operationID)
                        }
                    },
                    reject: {
                        Task {
                            await viewModel.reject(runID: plan.runID)
                        }
                    }
                )
            }
        }
    }
}

private struct ApprovalOperationRow: View {
    let runID: String
    let operation: WriteOperation
    let approve: () -> Void
    let reject: () -> Void

    var body: some View {
        HStack(alignment: .center, spacing: 18) {
            Circle()
                .fill(statusColor)
                .frame(width: 8, height: 8)
            iconBox
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline) {
                    Text("Write Plan")
                        .font(.system(size: 16, weight: .semibold))
                    Spacer()
                    Text(timeLabel)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Text(operation.preview)
                    .font(.system(size: 14))
                Text(operationSubtitle)
                    .font(.system(size: 13))
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                HStack(spacing: 8) {
                    Label("Evidence \(evidenceCount)", systemImage: "paperclip")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(
                            Capsule()
                                .strokeBorder(Color(nsColor: .separatorColor).opacity(0.55), lineWidth: 1)
                        )
                    Text(operation.operationType)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            HStack(spacing: 10) {
                Button {
                    approve()
                } label: {
                    Label("Approve", systemImage: "checkmark")
                        .foregroundStyle(.green)
                }
                .buttonStyle(.bordered)
                .disabled(operation.approvalStatus != "pending")

                Button {
                    reject()
                } label: {
                    Label("Reject", systemImage: "xmark")
                        .foregroundStyle(.red)
                }
                .buttonStyle(.bordered)
                .disabled(operation.approvalStatus != "pending")
            }
        }
        .padding(.vertical, 26)
    }

    private var iconBox: some View {
        RoundedRectangle(cornerRadius: 10, style: .continuous)
            .strokeBorder(Color(nsColor: .separatorColor).opacity(0.6), lineWidth: 1)
            .background(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(Color(nsColor: .controlBackgroundColor))
            )
            .frame(width: 44, height: 44)
            .overlay(
                Image(systemName: operationIcon)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundStyle(.orange)
            )
    }

    private var operationIcon: String {
        if operation.operationType.contains("task") {
            return "checkmark.square"
        }
        if operation.operationType.contains("im.") {
            return "bubble.left"
        }
        return "doc.text"
    }

    private var statusColor: Color {
        operation.approvalStatus == "pending" ? .orange : .green
    }

    private var operationSubtitle: String {
        if !operation.target.isEmpty {
            return "Target: \(render(operation.target))"
        }
        return "Run \(runID)"
    }

    private var evidenceCount: Int {
        let text = operation.dryRunPayload.values.map(\.description).joined(separator: "\n")
        return max(text.components(separatedBy: "seg-").count - 1, 0)
    }

    private var timeLabel: String {
        operation.approvalStatus == "pending" ? "Pending" : operation.approvalStatus.capitalized
    }

    private func render(_ values: [String: JSONValue]) -> String {
        values.map { "\($0.key)=\($0.value)" }.sorted().joined(separator: ", ")
    }
}
