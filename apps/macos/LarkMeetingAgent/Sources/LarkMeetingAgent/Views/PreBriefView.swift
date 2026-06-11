import LarkMeetingAgentCore
import SwiftUI

struct PreBriefView: View {
    let preBrief: PreBrief?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Pre-brief")
                .font(.headline)
            if let preBrief {
                Text(preBrief.goal)
                    .font(.subheadline)
                ForEach(preBrief.sections, id: \.title) { section in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(section.title)
                            .font(.caption)
                            .fontWeight(.semibold)
                        ForEach(section.bullets, id: \.self) { bullet in
                            Text("- \(bullet)")
                                .font(.caption)
                        }
                        ForEach(section.sources, id: \.sourceID) { source in
                            Text("Source: \(source.sourceLabel)")
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                    }
                }
                if !preBrief.warnings.isEmpty {
                    Text("Warnings: \(preBrief.warnings.joined(separator: ", "))")
                        .font(.caption)
                        .foregroundStyle(.orange)
                }
            } else {
                Text("Generate a pre-brief from the backend.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
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
