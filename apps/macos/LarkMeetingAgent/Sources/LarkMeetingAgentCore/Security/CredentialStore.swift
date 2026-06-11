import Foundation
import Security

public protocol CredentialStore: Sendable {
    func loadToken() throws -> String?
    func saveToken(_ token: String) throws
    func deleteToken() throws
}

public final class InMemoryCredentialStore: CredentialStore, @unchecked Sendable {
    private var token: String?

    public init(token: String? = nil) {
        self.token = token
    }

    public func loadToken() throws -> String? {
        token
    }

    public func saveToken(_ token: String) throws {
        self.token = token
    }

    public func deleteToken() throws {
        token = nil
    }
}

public final class KeychainCredentialStore: CredentialStore, @unchecked Sendable {
    private let service: String
    private let account: String

    public init(service: String = "com.larkmeetingagent.companion", account: String = "bearer-token") {
        self.service = service
        self.account = account
    }

    public func loadToken() throws -> String? {
        var query = baseQuery()
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        if status == errSecItemNotFound {
            return nil
        }
        guard status == errSecSuccess else {
            throw KeychainError.status(status)
        }
        guard let data = item as? Data else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    public func saveToken(_ token: String) throws {
        let data = Data(token.utf8)
        var query = baseQuery()
        let attributes = [kSecValueData as String: data]
        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if updateStatus == errSecSuccess {
            return
        }
        if updateStatus != errSecItemNotFound {
            throw KeychainError.status(updateStatus)
        }
        query[kSecValueData as String] = data
        let addStatus = SecItemAdd(query as CFDictionary, nil)
        guard addStatus == errSecSuccess else {
            throw KeychainError.status(addStatus)
        }
    }

    public func deleteToken() throws {
        let status = SecItemDelete(baseQuery() as CFDictionary)
        if status != errSecSuccess && status != errSecItemNotFound {
            throw KeychainError.status(status)
        }
    }

    private func baseQuery() -> [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
    }
}

public enum KeychainError: Error, Equatable, Sendable {
    case status(OSStatus)
}
