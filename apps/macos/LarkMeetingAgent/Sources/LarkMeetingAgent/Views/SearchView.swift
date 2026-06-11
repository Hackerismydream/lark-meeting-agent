import LarkMeetingAgentCore
import SwiftUI

struct SearchView: View {
    @ObservedObject var viewModel: SearchUploadViewModel
    @Binding var question: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Search")
                .font(.headline)
            TextField("Ask across meetings", text: $question)
            Button("Search memory") {
                Task {
                    await viewModel.search(question: question)
                }
            }
            if let answer = viewModel.answer {
                Text(answer.sufficient ? answer.answer : "Insufficient evidence")
                    .font(.caption)
                ForEach(answer.sources, id: \.sourceKey) { source in
                    SourceCitationView(source: source)
                }
            }
        }
    }
}

private extension SourceCitation {
    var sourceKey: String {
        [meetingID, segmentID, timestamp, text].compactMap { $0 }.joined(separator: "-")
    }
}
