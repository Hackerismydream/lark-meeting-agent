import LarkMeetingAgentCore
import SwiftUI

struct WriteOperationDetailView: View {
    let operation: WriteOperation

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(operation.preview)
                .font(.subheadline)
                .fontWeight(.medium)
            Text("\(operation.operationType.localizedOperationType) · \(operation.operationID)")
                .font(.caption)
                .foregroundStyle(.secondary)
            if !operation.target.isEmpty {
                Text("目标：\(render(operation.target))")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            Text("审批：\(operation.approvalStatus.localizedApprovalStatus) · 执行：\(operation.executionStatus.localizedExecutionStatus)")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private func render(_ values: [String: JSONValue]) -> String {
        values.map { "\($0.key)=\($0.value)" }.sorted().joined(separator: ", ")
    }
}

private extension String {
    var localizedOperationType: String {
        switch self {
        case "docs.create":
            return "创建文档"
        case "task.create":
            return "创建任务"
        case "im.send":
            return "发送群消息"
        case "calendar.create":
            return "创建日程"
        case "vc.join":
            return "加入会议"
        case "vc.leave":
            return "离开会议"
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
