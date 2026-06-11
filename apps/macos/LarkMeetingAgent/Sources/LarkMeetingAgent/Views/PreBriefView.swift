import LarkMeetingAgentCore
import SwiftUI

struct PreBriefView: View {
    let preBrief: PreBrief?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let preBrief {
                HStack(spacing: 8) {
                    Image(systemName: "doc.text.magnifyingglass")
                        .foregroundStyle(.blue)
                    Text(preBrief.goal)
                        .font(.system(size: 15, weight: .semibold))
                }
                ForEach(preBrief.sections, id: \.title) { section in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(section.title)
                            .font(.system(size: 13))
                            .fontWeight(.semibold)
                        ForEach(section.bullets, id: \.self) { bullet in
                            Text("• \(bullet)")
                                .font(.system(size: 13))
                        }
                        ForEach(section.sources, id: \.sourceID) { source in
                            SourceCitationView(source: source)
                                .padding(8)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(
                                    RoundedRectangle(cornerRadius: 8, style: .continuous)
                                        .fill(Color(nsColor: .controlBackgroundColor))
                                )
                        }
                    }
                    .padding(.vertical, 4)
                }
                if !preBrief.warnings.isEmpty {
                    Text("提醒：\(preBrief.warnings.joined(separator: "，"))")
                        .font(.caption)
                        .foregroundStyle(.orange)
                }
            } else {
                Text("输入会议主题或项目名称，生成会前简报。")
                    .font(.caption)
                    .foregroundStyle(.secondary)
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
}

private extension SourceCitation {
    var sourceID: String {
        [meetingID, segmentID, timestamp, text].compactMap { $0 }.joined(separator: "-")
    }

    var sourceLabel: String {
        [meetingID, segmentID, speakerName, timestamp].compactMap { $0 }.joined(separator: " / ")
    }
}
