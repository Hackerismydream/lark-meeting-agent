import Foundation

public struct APIEnvelope<T: Decodable & Sendable>: Decodable, Sendable {
    public let ok: Bool
    public let data: T?
    public let error: APIError?
}

public struct APIError: Decodable, Equatable, Sendable {
    public let code: String
    public let message: String
}

public struct AgentStatus: Decodable, Equatable, Sendable {
    public let status: String
    public let service: String
    public let companionApi: String
    public let providerMode: String
    public let analyzerMode: String
    public let storage: String

    enum CodingKeys: String, CodingKey {
        case status
        case service
        case companionApi = "companion_api"
        case providerMode = "provider_mode"
        case analyzerMode = "analyzer_mode"
        case storage
    }
}

public enum ConnectionState: Equatable, Sendable {
    case disconnected
    case connecting
    case connected(AgentStatus)
    case failed(String)
}

public struct PendingWritePlansResponse: Decodable, Equatable, Sendable {
    public let items: [PendingWritePlan]
}

public struct PendingWritePlan: Decodable, Identifiable, Equatable, Sendable {
    public let runID: String
    public let status: String
    public let operations: [WriteOperation]

    public var id: String { runID }

    enum CodingKeys: String, CodingKey {
        case runID = "run_id"
        case status
        case operations
    }
}

public struct WriteOperation: Decodable, Identifiable, Equatable, Sendable {
    public let operationID: String
    public let operationType: String
    public let target: [String: JSONValue]
    public let dryRunPayload: [String: JSONValue]
    public let preview: String
    public let requiresApproval: Bool
    public let approvalStatus: String
    public let executionStatus: String

    public var id: String { operationID }

    enum CodingKeys: String, CodingKey {
        case operationID = "operation_id"
        case operationType = "operation_type"
        case target
        case dryRunPayload = "dry_run_payload"
        case preview
        case requiresApproval = "requires_approval"
        case approvalStatus = "approval_status"
        case executionStatus = "execution_status"
    }
}

public enum JSONValue: Decodable, Equatable, Sendable, CustomStringConvertible {
    case string(String)
    case number(Double)
    case bool(Bool)
    case object([String: JSONValue])
    case array([JSONValue])
    case null

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Double.self) {
            self = .number(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([JSONValue].self) {
            self = .array(value)
        } else {
            self = .object(try container.decode([String: JSONValue].self))
        }
    }

    public var description: String {
        switch self {
        case .string(let value):
            return value
        case .number(let value):
            return String(value)
        case .bool(let value):
            return String(value)
        case .object(let value):
            return value.map { "\($0.key): \($0.value)" }.sorted().joined(separator: ", ")
        case .array(let value):
            return value.map(\.description).joined(separator: ", ")
        case .null:
            return "null"
        }
    }
}
