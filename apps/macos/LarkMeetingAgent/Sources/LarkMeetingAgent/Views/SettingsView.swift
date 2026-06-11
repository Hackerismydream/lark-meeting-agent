import LarkMeetingAgentCore
import SwiftUI

struct SettingsView: View {
    @ObservedObject var viewModel: StatusViewModel
    @State private var apiBaseURL: String = ""
    @State private var environmentLabel: String = ""
    @State private var notificationsEnabled: Bool = true

    var body: some View {
        Form {
            TextField("API Base URL", text: $apiBaseURL)
            TextField("Environment", text: $environmentLabel)
            Toggle("Notifications", isOn: $notificationsEnabled)
            if environmentLabel.localizedCaseInsensitiveContains("prod") {
                Text("Production backend: approvals will affect real collaboration systems after backend confirmation.")
                    .foregroundStyle(.orange)
            }
            Button("Save") {
                if let url = URL(string: apiBaseURL) {
                    viewModel.saveSettings(apiBaseURL: url, environmentLabel: environmentLabel, notificationsEnabled: notificationsEnabled)
                }
            }
        }
        .padding()
        .frame(width: 420)
        .onAppear {
            apiBaseURL = viewModel.settings.apiBaseURL.absoluteString
            environmentLabel = viewModel.settings.environmentLabel
            notificationsEnabled = viewModel.settings.notificationsEnabled
        }
    }
}
