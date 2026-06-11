import Foundation
import LarkMeetingAgentCore

@main
struct SmokeTests {
    static func main() async throws {
        try await statusDecodesEnvelopeAndSendsBearerToken()
        try inMemoryCredentialStoreRoundTripsToken()
        print("LarkMeetingAgentCore smoke tests passed")
    }

    private static func statusDecodesEnvelopeAndSendsBearerToken() async throws {
        let transport = MockTransport(
            data: """
            {
              "ok": true,
              "data": {
                "status": "ok",
                "service": "lark-meeting-agent",
                "companion_api": "v1",
                "provider_mode": "fake",
                "analyzer_mode": "fake",
                "storage": "SQLiteMeetingRepository"
              },
              "error": null
            }
            """.data(using: .utf8)!
        )
        let client = AgentAPIClient(
            baseURL: URL(string: "http://127.0.0.1:8765")!,
            bearerTokenProvider: { "dev-token" },
            transport: transport
        )

        let status = try await client.status()

        try assert(status.providerMode == "fake", "expected fake provider mode")
        try assert(
            transport.lastRequest?.value(forHTTPHeaderField: "Authorization") == "Bearer dev-token",
            "expected bearer token header"
        )
    }

    private static func inMemoryCredentialStoreRoundTripsToken() throws {
        let store = InMemoryCredentialStore()

        try store.saveToken("secret")
        let savedToken = try store.loadToken()
        try assert(savedToken == "secret", "expected saved token")
        try store.deleteToken()
        let deletedToken = try store.loadToken()
        try assert(deletedToken == nil, "expected deleted token")
    }

    private static func assert(_ condition: @autoclosure () -> Bool, _ message: String) throws {
        if !condition() {
            throw SmokeTestError.assertionFailed(message)
        }
    }
}

private final class MockTransport: HTTPTransport, @unchecked Sendable {
    let data: Data
    var lastRequest: URLRequest?

    init(data: Data) {
        self.data = data
    }

    func data(for request: URLRequest) async throws -> (Data, URLResponse) {
        lastRequest = request
        return (data, HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!)
    }
}

private enum SmokeTestError: Error {
    case assertionFailed(String)
}
