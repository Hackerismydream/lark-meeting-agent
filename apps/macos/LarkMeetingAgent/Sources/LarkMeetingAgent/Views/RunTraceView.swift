import LarkMeetingAgentCore
import SwiftUI

struct RunTraceView: View {
    let runs: [RunDetail]
    let selectedRun: RunDetail?
    let trace: RunTrace?
    let inspectRun: (String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Runs")
                .font(.system(size: 15, weight: .semibold))
            if runs.isEmpty {
                Text("No runs from backend")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                ForEach(runs) { run in
                    Button {
                        inspectRun(run.runID)
                    } label: {
                        HStack {
                            Image(systemName: run.status == "completed" ? "checkmark.circle.fill" : "clock")
                                .foregroundStyle(run.status == "completed" ? .green : .orange)
                            Text("\(run.runID) - \(run.status)")
                                .lineLimit(1)
                            Spacer()
                        }
                    }
                    .buttonStyle(.plain)
                    .padding(.vertical, 5)
                }
            }
            if let selectedRun {
                Divider()
                Text("Run \(selectedRun.runID)")
                    .font(.subheadline)
                Text("Status: \(selectedRun.status)")
                    .font(.caption)
                ForEach(selectedRun.errors, id: \.self) { error in
                    Text("Error: \(error)")
                        .font(.caption)
                        .foregroundStyle(.red)
                }
                if let operations = selectedRun.writePlan?.operations, !operations.isEmpty {
                    Text("Write results")
                        .font(.caption)
                        .fontWeight(.semibold)
                    ForEach(operations) { operation in
                        Text("\(operation.operationID): \(operation.approvalStatus) / \(operation.executionStatus)")
                            .font(.caption)
                    }
                }
            }
            if let trace {
                Divider()
                Text("\(trace.workflow) trace")
                    .font(.caption)
                    .fontWeight(.semibold)
                ForEach(trace.events) { event in
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(event.stage): \(event.message)")
                            .font(.caption)
                        if !event.data.isEmpty {
                            Text(render(event.data))
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                                .lineLimit(3)
                        }
                    }
                }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(nsColor: .textBackgroundColor))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .strokeBorder(Color(nsColor: .separatorColor).opacity(0.45), lineWidth: 1)
        )
    }

    private func render(_ values: [String: JSONValue]) -> String {
        values.map { "\($0.key)=\($0.value)" }.sorted().joined(separator: ", ")
    }
}
