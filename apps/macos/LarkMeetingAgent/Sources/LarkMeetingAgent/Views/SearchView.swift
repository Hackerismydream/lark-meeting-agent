import LarkMeetingAgentCore
import SwiftUI

struct SearchView: View {
    @ObservedObject var viewModel: SearchUploadViewModel
    @State private var question = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Search")
                    .font(.system(size: 22, weight: .semibold))
                Text("Ask across meeting memory and require source citations.")
                    .font(.system(size: 14))
                    .foregroundStyle(.secondary)
            }
            HStack(spacing: 10) {
                TextField("Ask across meetings", text: $question)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit {
                        Task {
                            await viewModel.search(question: question)
                        }
                    }
                Button {
                    Task {
                        await viewModel.search(question: question)
                    }
                } label: {
                    Label("Search memory", systemImage: "magnifyingglass")
                }
                .buttonStyle(.borderedProminent)
            }
            if viewModel.isLoading {
                ProgressView()
            }
            if let answer = viewModel.answer {
                answerView(answer)
            }
        }
    }

    private func answerView(_ answer: QAAnswer) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 8) {
                Image(systemName: answer.sufficient ? "checkmark.seal.fill" : "exclamationmark.triangle.fill")
                    .foregroundStyle(answer.sufficient ? .green : .orange)
                Text(answer.sufficient ? "Answer" : "Insufficient evidence")
                    .font(.system(size: 15, weight: .semibold))
            }
            Text(answer.sufficient ? answer.answer : "No source-backed answer was found for this question.")
                .font(.system(size: 14))
            if !answer.sources.isEmpty {
                Divider()
                Text("Sources")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
                ForEach(answer.sources, id: \.sourceKey) { source in
                    SourceCitationView(source: source)
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .fill(Color(nsColor: .controlBackgroundColor))
                        )
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
}

private extension SourceCitation {
    var sourceKey: String {
        [meetingID, segmentID, timestamp, text].compactMap { $0 }.joined(separator: "-")
    }
}
