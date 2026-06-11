import LarkMeetingAgentCore
import SwiftUI

struct WriteOperationDetailView: View {
    let operation: WriteOperation

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(operation.preview)
                .font(.subheadline)
                .fontWeight(.medium)
            Text("\(operation.operationType) · \(operation.operationID)")
                .font(.caption)
                .foregroundStyle(.secondary)
            if !operation.target.isEmpty {
                Text("Target: \(render(operation.target))")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            Text("Approval: \(operation.approvalStatus) · Execution: \(operation.executionStatus)")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private func render(_ values: [String: JSONValue]) -> String {
        values.map { "\($0.key)=\($0.value)" }.sorted().joined(separator: ", ")
    }
}
