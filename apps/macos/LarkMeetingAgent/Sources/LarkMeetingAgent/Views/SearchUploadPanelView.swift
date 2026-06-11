import LarkMeetingAgentCore
import SwiftUI

struct SearchUploadPanelView: View {
    @StateObject private var viewModel = SearchUploadViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            SearchView(viewModel: viewModel)
            Divider()
            UploadTranscriptView(viewModel: viewModel)
            if viewModel.isLoading {
                ProgressView()
            }
            if let message = viewModel.message {
                Text(message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
