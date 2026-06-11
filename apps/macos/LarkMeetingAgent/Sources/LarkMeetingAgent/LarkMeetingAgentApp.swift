import LarkMeetingAgentCore
import SwiftUI

@main
struct LarkMeetingAgentApp: App {
    @StateObject private var viewModel = StatusViewModel()

    var body: some Scene {
        WindowGroup("Lark Meeting Agent") {
            StatusView(viewModel: viewModel)
        }
        MenuBarExtra("Lark Meeting Agent", systemImage: "waveform.and.person.filled") {
            StatusView(viewModel: viewModel)
        }
        Settings {
            SettingsView(viewModel: viewModel)
        }
    }
}
