import LarkMeetingAgentCore
import SwiftUI

struct StatusView: View {
    @ObservedObject var viewModel: StatusViewModel
    @StateObject private var searchUploadViewModel = SearchUploadViewModel()
    @State private var settingsPresented = false
    @State private var selectedSection: WorkspaceSection = .upload

    var body: some View {
        VStack(spacing: 0) {
            topBar
            Divider()
            HStack(spacing: 0) {
                ScrollView {
                    mainContent
                        .padding(.horizontal, 28)
                        .padding(.vertical, 26)
                }
                .background(Color(nsColor: .windowBackgroundColor))
                Divider()
                MeetingSummaryRailView(
                    connectionState: viewModel.connectionState,
                    pendingApprovalCount: viewModel.pendingApprovalCount,
                    selectedSection: selectedSection.title,
                    settingsPresented: $settingsPresented
                )
            }
        }
        .frame(minWidth: 980, minHeight: 640)
        .background(Color(nsColor: .windowBackgroundColor))
        .task {
            await viewModel.refreshStatus()
        }
        .sheet(isPresented: $settingsPresented) {
            SettingsView(viewModel: viewModel)
        }
        .onReceive(NotificationCenter.default.publisher(for: .larkMeetingAgentRunsChanged)) { _ in
            Task {
                await viewModel.refreshStatus()
            }
        }
    }

    private var topBar: some View {
        ZStack {
            HStack {
                Spacer()
                Button {
                    Task {
                        await viewModel.refreshStatus()
                    }
                } label: {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .buttonStyle(.bordered)
            }
            .padding(.horizontal, 28)

            Picker("", selection: $selectedSection) {
                ForEach(WorkspaceSection.allCases) { section in
                    Text(section.title).tag(section)
                }
            }
            .pickerStyle(.segmented)
            .labelsHidden()
            .frame(width: 520)
        }
        .padding(.vertical, 12)
    }

    @ViewBuilder
    private var mainContent: some View {
        switch selectedSection {
        case .approvals:
            ApprovalInboxView()
        case .preBrief:
            PreBriefTracePanelView()
        case .search:
            SearchView(viewModel: searchUploadViewModel)
        case .upload:
            UploadTranscriptView(viewModel: searchUploadViewModel)
            if searchUploadViewModel.isLoading {
                ProgressView()
                    .padding(.top, 12)
            }
            if let message = searchUploadViewModel.message {
                Text(message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.top, 8)
            }
        }
    }

    private var statusText: String {
        switch viewModel.connectionState {
        case .disconnected:
            return "Disconnected"
        case .connecting:
            return "Connecting..."
        case .connected(let status):
            return "Connected: \(status.environmentSummary)"
        case .failed:
            return "Disconnected"
        }
    }

    private var statusColor: Color {
        switch viewModel.connectionState {
        case .connected:
            return .green
        case .connecting:
            return .orange
        case .disconnected, .failed:
            return .red
        }
    }
}

enum WorkspaceSection: String, CaseIterable, Identifiable {
    case upload
    case approvals
    case search
    case preBrief

    var id: String { rawValue }

    var title: String {
        switch self {
        case .upload:
            return "Upload"
        case .approvals:
            return "Approvals"
        case .search:
            return "Search"
        case .preBrief:
            return "Pre-brief"
        }
    }
}

private extension AgentStatus {
    var environmentSummary: String {
        "\(providerMode) / \(storage)"
    }
}
