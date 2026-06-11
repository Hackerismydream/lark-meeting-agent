import LarkMeetingAgentCore
import SwiftUI

@main
struct LarkMeetingAgentApp: App {
    @StateObject private var viewModel = StatusViewModel()

    var body: some Scene {
        MenuBarExtra("Lark Meeting Agent", systemImage: "waveform.and.person.filled") {
            StatusView(viewModel: viewModel)
        }
        Settings {
            SettingsView(viewModel: viewModel)
        }
    }
}
