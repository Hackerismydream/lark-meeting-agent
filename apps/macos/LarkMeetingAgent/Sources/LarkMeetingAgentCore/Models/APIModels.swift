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
