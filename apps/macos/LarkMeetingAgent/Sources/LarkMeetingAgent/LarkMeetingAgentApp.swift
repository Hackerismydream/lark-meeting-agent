import LarkMeetingAgentCore
import SwiftUI

@main
struct LarkMeetingAgentApp: App {
    @StateObject private var viewModel = StatusViewModel()

    var body: some Scene {
        WindowGroup("飞书会议智能体") {
            StatusView(viewModel: viewModel)
        }
        MenuBarExtra("飞书会议智能体", systemImage: "waveform.and.person.filled") {
            StatusView(viewModel: viewModel)
        }
        Settings {
            SettingsView(viewModel: viewModel)
        }
    }
}
