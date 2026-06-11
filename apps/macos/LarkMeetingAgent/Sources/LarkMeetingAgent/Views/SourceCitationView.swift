import LarkMeetingAgentCore
import SwiftUI

struct SourceCitationView: View {
    let source: SourceCitation

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text([source.meetingID, source.segmentID].compactMap { $0 }.joined(separator: " / "))
                .font(.caption)
                .fontWeight(.semibold)
            Text([source.speakerName, source.timestamp].compactMap { $0 }.joined(separator: " @ "))
                .font(.caption2)
                .foregroundStyle(.secondary)
            if let text = source.text {
                Text(text)
                    .font(.caption2)
                    .lineLimit(3)
            }
        }
    }
}
