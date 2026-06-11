import Foundation
import LarkMeetingAgentCore

@main
struct SmokeTests {
    static func main() async throws {
        try await statusDecodesEnvelopeAndSendsBearerToken()
        try await pendingPlansDecodeAndApproveSendsExplicitOperationIDs()
        try await preBriefRunsAndTraceDecode()
        try inMemoryCredentialStoreRoundTripsToken()
        print("LarkMeetingAgentCore smoke tests passed")
    }

    private static func preBriefRunsAndTraceDecode() async throws {
        let transport = MockTransport(
            data: """
            {
              "ok": true,
              "data": {
                "run_id": "prebrief-1",
                "meeting_type": "general",
                "goal": "Prepare customer review",
                "sections": [
                  {
                    "title": "Context",
                    "bullets": ["Review open risks"],
                    "sources": [
                      {
                        "meeting_id": "m-1",
                        "segment_id": "s1",
                        "kind": "segment",
                        "text": "Risk was discussed",
                        "speaker_name": "Alice",
                        "timestamp": "00:01"
                      }
                    ]
                  }
                ],
                "suggested_questions": ["What changed?"],
                "warnings": [],
                "trace_path": ".lark_meeting_agent/traces/prebrief-1.json"
              },
              "error": null
            }
            """.data(using: .utf8)!
        )
        let client = AgentAPIClient(baseURL: URL(string: "http://127.0.0.1:8765")!, bearerTokenProvider: { nil }, transport: transport)

        let brief = try await client.preBrief(query: "customer", meetingID: nil, meetingType: "general", project: nil, customer: nil)

        try assert(brief.runID == "prebrief-1", "expected prebrief run")
        try assert(brief.sections.first?.sources.first?.segmentID == "s1", "expected source citation")

        transport.data = """
        {
          "ok": true,
          "data": {
            "items": [
              {
                "run_id": "run-1",
                "status": "approval_required",
                "provider_mode": "fake",
                "analyzer_mode": "fake",
                "write_plan": {
                  "run_id": "run-1",
                  "status": "approval_required",
                  "operations": []
                },
                "errors": [],
                "created_at": "2026-06-11T00:00:00Z",
                "updated_at": "2026-06-11T00:00:00Z"
              }
            ]
          },
          "error": null
        }
        """.data(using: .utf8)!
        let runs = try await client.runs()
        try assert(runs.first?.runID == "run-1", "expected run list")

        transport.data = """
        {
          "ok": true,
          "data": {
            "run_id": "run-1",
            "workflow": "PostMeetingWorkflow",
            "events": [
              {
                "event_id": "evt-1",
                "stage": "analyze",
                "message": "structured extraction complete",
                "data": {"tool": "fake"},
                "timestamp": "2026-06-11T00:00:00Z"
              }
            ],
            "created_at": "2026-06-11T00:00:00Z"
          },
          "error": null
        }
        """.data(using: .utf8)!
        let trace = try await client.trace(runID: "run-1")
        try assert(trace.events.first?.stage == "analyze", "expected trace event")
    }

    private static func pendingPlansDecodeAndApproveSendsExplicitOperationIDs() async throws {
        let transport = MockTransport(
            data: """
            {
              "ok": true,
              "data": {
                "items": [
                  {
                    "run_id": "run-1",
                    "status": "approval_required",
                    "operations": [
                      {
                        "operation_id": "op-doc-1",
                        "operation_type": "docs.create",
                        "target": {"folder_token": null},
                        "dry_run_payload": {"title": "Demo"},
                        "preview": "Create doc",
                        "requires_approval": true,
                        "approval_status": "pending",
                        "execution_status": "pending"
                      }
                    ]
                  }
                ]
              },
              "error": null
            }
            """.data(using: .utf8)!
        )
        let client = AgentAPIClient(baseURL: URL(string: "http://127.0.0.1:8765")!, bearerTokenProvider: { nil }, transport: transport)

        let plans = try await client.pendingWritePlans()

        try assert(plans.first?.runID == "run-1", "expected pending run")
        try assert(plans.first?.operations.first?.operationID == "op-doc-1", "expected operation")

        transport.data = """
        {"ok": true, "data": {"run_id": "run-1"}, "error": null}
        """.data(using: .utf8)!
        try await client.approve(runID: "run-1", operationIDs: ["op-doc-1"])

        try assert(transport.lastRequest?.url?.path == "/v1/runs/run-1/approve", "expected approve path")
        let body = try JSONSerialization.jsonObject(with: transport.lastRequest?.httpBody ?? Data()) as? [String: Any]
        try assert((body?["operation_ids"] as? [String]) == ["op-doc-1"], "expected explicit operation_ids body")
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
    var data: Data
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
