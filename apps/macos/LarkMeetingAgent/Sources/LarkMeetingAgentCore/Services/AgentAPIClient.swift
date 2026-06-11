import Foundation

public protocol HTTPTransport: Sendable {
    func data(for request: URLRequest) async throws -> (Data, URLResponse)
}

public struct URLSessionTransport: HTTPTransport {
    public init() {}

    public func data(for request: URLRequest) async throws -> (Data, URLResponse) {
        try await URLSession.shared.data(for: request)
    }
}

public final class AgentAPIClient: Sendable {
    private let baseURL: URL
    private let bearerTokenProvider: @Sendable () -> String?
    private let transport: HTTPTransport

    public init(baseURL: URL, bearerTokenProvider: @escaping @Sendable () -> String?, transport: HTTPTransport = URLSessionTransport()) {
        self.baseURL = baseURL
        self.bearerTokenProvider = bearerTokenProvider
        self.transport = transport
    }

    public func status() async throws -> AgentStatus {
        let envelope: APIEnvelope<AgentStatus> = try await get("/v1/agent/status")
        if let data = envelope.data, envelope.ok {
            return data
        }
        throw AgentAPIError.api(envelope.error ?? APIError(code: "unknown", message: "Unknown API error"))
    }

    public func pendingWritePlans() async throws -> [PendingWritePlan] {
        let envelope: APIEnvelope<PendingWritePlansResponse> = try await get("/v1/write-plans/pending")
        if let data = envelope.data, envelope.ok {
            return data.items
        }
        throw AgentAPIError.api(envelope.error ?? APIError(code: "unknown", message: "Unknown API error"))
    }

    public func approve(runID: String, operationIDs: [String]) async throws {
        let body = ApproveBody(operationIDs: operationIDs)
        let envelope: APIEnvelope<JSONValue> = try await post("/v1/runs/\(runID)/approve", body: body)
        if !envelope.ok {
            throw AgentAPIError.api(envelope.error ?? APIError(code: "unknown", message: "Unknown API error"))
        }
    }

    public func reject(runID: String, reason: String? = nil) async throws {
        let body = RejectBody(reason: reason)
        let envelope: APIEnvelope<JSONValue> = try await post("/v1/runs/\(runID)/reject", body: body)
        if !envelope.ok {
            throw AgentAPIError.api(envelope.error ?? APIError(code: "unknown", message: "Unknown API error"))
        }
    }

    private func get<T: Decodable & Sendable>(_ path: String) async throws -> APIEnvelope<T> {
        try await request("GET", path: path)
    }

    private func post<T: Decodable & Sendable, Body: Encodable & Sendable>(_ path: String, body: Body) async throws -> APIEnvelope<T> {
        try await request("POST", path: path, body: JSONEncoder().encode(body))
    }

    private func request<T: Decodable & Sendable>(_ method: String, path: String, body: Data? = nil) async throws -> APIEnvelope<T> {
        var request = URLRequest(url: baseURL.appendingPathComponent(path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))))
        request.httpMethod = method
        request.httpBody = body
        if body != nil {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        if let token = bearerTokenProvider(), !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        let (data, response) = try await transport.data(for: request)
        if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
            throw AgentAPIError.httpStatus(http.statusCode)
        }
        return try JSONDecoder().decode(APIEnvelope<T>.self, from: data)
    }
}

public enum AgentAPIError: Error, Equatable {
    case httpStatus(Int)
    case api(APIError)
}

private struct ApproveBody: Encodable, Sendable {
    let operationIDs: [String]

    enum CodingKeys: String, CodingKey {
        case operationIDs = "operation_ids"
    }
}

private struct RejectBody: Encodable, Sendable {
    let reason: String?
}
