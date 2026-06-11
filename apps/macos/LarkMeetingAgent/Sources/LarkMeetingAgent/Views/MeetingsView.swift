import LarkMeetingAgentCore
import SwiftUI

struct MeetingsView: View {
    let meetings: [MeetingSummary]
    let source: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("今日会议")
                    .font(.system(size: 15, weight: .semibold))
                if let source {
                    Text(source)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            if meetings.isEmpty {
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "calendar")
                        .foregroundStyle(.secondary)
                    VStack(alignment: .leading, spacing: 3) {
                        Text("暂未连接日历")
                            .font(.caption)
                            .fontWeight(.medium)
                        Text("你可以先在“上传”中导入会议转写；如果已有本地运行记录，也可以在下方输入查询生成简报。")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            } else {
                ForEach(meetings) { meeting in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(meeting.title ?? "未命名会议")
                            .font(.subheadline)
                        Text([meeting.startTime, meeting.endTime].compactMap { $0 }.joined(separator: " - "))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(nsColor: .textBackgroundColor))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .strokeBorder(Color(nsColor: .separatorColor).opacity(0.45), lineWidth: 1)
        )
    }
}
