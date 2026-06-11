import LarkMeetingAgentCore
import SwiftUI

struct RunTraceView: View {
    let runs: [RunDetail]
    let selectedRun: RunDetail?
    let trace: RunTrace?
    let inspectRun: (String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("运行记录")
                .font(.system(size: 15, weight: .semibold))
            if runs.isEmpty {
                Text("暂无运行记录")
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
                            Text("\(run.runID) - \(run.status.localizedRunStatus)")
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
                Text("运行 \(selectedRun.runID)")
                    .font(.subheadline)
                Text("状态：\(selectedRun.status.localizedRunStatus)")
                    .font(.caption)
                ForEach(selectedRun.errors, id: \.self) { error in
                    Text("错误：\(error)")
                        .font(.caption)
                        .foregroundStyle(.red)
                }
                if let operations = selectedRun.writePlan?.operations, !operations.isEmpty {
                    Text("写入结果")
                        .font(.caption)
                        .fontWeight(.semibold)
                    ForEach(operations) { operation in
                        Text("\(operation.operationID)：\(operation.approvalStatus.localizedApprovalStatus) / \(operation.executionStatus.localizedExecutionStatus)")
                            .font(.caption)
                    }
                }
            }
            if let trace {
                Divider()
                Text("\(trace.workflow) 运行轨迹")
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

private extension String {
    var localizedRunStatus: String {
        switch self {
        case "completed":
            return "已完成"
        case "approval_required":
            return "待审批"
        case "failed":
            return "失败"
        case "running":
            return "运行中"
        default:
            return self
        }
    }

    var localizedApprovalStatus: String {
        switch self {
        case "approved":
            return "已批准"
        case "rejected":
            return "已拒绝"
        case "pending":
            return "待审批"
        default:
            return self
        }
    }

    var localizedExecutionStatus: String {
        switch self {
        case "completed":
            return "已完成"
        case "skipped":
            return "已跳过"
        case "pending":
            return "待执行"
        case "failed":
            return "失败"
        default:
            return self
        }
    }
}
