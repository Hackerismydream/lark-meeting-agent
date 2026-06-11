import LarkMeetingAgentCore
import SwiftUI

struct MeetingsView: View {
    let meetings: [MeetingSummary]
    let source: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("Today")
                    .font(.headline)
                if let source {
                    Text(source)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            if meetings.isEmpty {
                Text("No meetings from backend")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                ForEach(meetings) { meeting in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(meeting.title ?? "Untitled meeting")
                            .font(.subheadline)
                        Text([meeting.startTime, meeting.endTime].compactMap { $0 }.joined(separator: " - "))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
    }
}
