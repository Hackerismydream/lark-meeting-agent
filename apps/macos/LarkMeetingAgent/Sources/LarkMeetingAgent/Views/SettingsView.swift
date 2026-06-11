import LarkMeetingAgentCore
import SwiftUI

struct SettingsView: View {
    @ObservedObject var viewModel: StatusViewModel
    @State private var apiBaseURL: String = ""
    @State private var environmentLabel: String = ""
    @State private var notificationsEnabled: Bool = true

    var body: some View {
        Form {
            TextField("API 地址", text: $apiBaseURL)
            TextField("环境", text: $environmentLabel)
            Toggle("通知", isOn: $notificationsEnabled)
            if environmentLabel.localizedCaseInsensitiveContains("prod") {
                Text("生产后端：审批后的写操作会在后端确认后影响真实协作系统。")
                    .foregroundStyle(.orange)
            }
            Button("保存") {
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
