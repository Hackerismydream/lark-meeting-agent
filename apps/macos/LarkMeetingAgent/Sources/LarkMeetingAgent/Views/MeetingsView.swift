import LarkMeetingAgentCore
import SwiftUI

struct MeetingsView: View {
    let meetings: [MeetingSummary]
    let source: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Today")
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
                        Text("Calendar is not connected yet")
                            .font(.caption)
                            .fontWeight(.medium)
                        Text("Use Upload to add meeting memory, or enter a query below to build a pre-brief from existing local runs.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
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
