import LarkMeetingAgentCore
import SwiftUI

struct ApprovalInboxView: View {
    @StateObject private var viewModel = ApprovalInboxViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Approvals")
                    .font(.headline)
                Spacer()
                Text("\(viewModel.pendingOperationCount)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            if viewModel.isLoading {
                ProgressView()
            } else if viewModel.plans.isEmpty {
                Text("No pending approvals")
                    .foregroundStyle(.secondary)
            } else {
                ForEach(viewModel.plans) { plan in
                    planView(plan)
                    Divider()
                }
            }
            if let message = viewModel.message {
                Text(message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Button("Refresh approvals") {
                Task {
                    await viewModel.refresh()
                }
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

    private func planView(_ plan: PendingWritePlan) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(plan.runID)
                .font(.caption)
                .foregroundStyle(.secondary)
            ForEach(plan.operations) { operation in
                Toggle(isOn: Binding(
                    get: {
                        viewModel.isSelected(runID: plan.runID, operationID: operation.operationID)
                    },
                    set: { isSelected in
                        viewModel.toggleSelection(runID: plan.runID, operationID: operation.operationID, isSelected: isSelected)
                    }
                )) {
                    WriteOperationDetailView(operation: operation)
                }
            }
            HStack {
                Button("Approve selected") {
                    Task {
                        await viewModel.approveSelected(runID: plan.runID)
                    }
                }
                .disabled(viewModel.selectedOperationIDsForRun(plan.runID).isEmpty)

                Button("Reject run") {
                    Task {
                        await viewModel.reject(runID: plan.runID)
                    }
                }
            }
        }
    }
}
