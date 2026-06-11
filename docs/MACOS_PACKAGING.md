# macOS Packaging

The V1.1 macOS app currently builds as a Swift Package executable for local development and manual QA.

## Local Build

```bash
swift build --package-path apps/macos/LarkMeetingAgent
swift run --package-path apps/macos/LarkMeetingAgent LarkMeetingAgent
```

Core smoke validation:

```bash
swift run --package-path apps/macos/LarkMeetingAgent LarkMeetingAgentCoreSmokeTests
```

Local `.app` bundle for manual QA and Computer Use:

```bash
scripts/build-macos-companion-app
open apps/macos/LarkMeetingAgent/.build/app/LarkMeetingAgent.app
```

This bundle is unsigned and intended for local development only.

## Xcode Build Status

On this workstation, `xcodebuild` is blocked because the active developer directory points to CommandLineTools instead of a full Xcode installation:

```text
xcode-select: error: tool 'xcodebuild' requires Xcode
```

After installing full Xcode, select it before running Xcode build validation:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
xcodebuild -scheme LarkMeetingAgent -destination 'platform=macOS' build
```

## Signing and Notarization

Signing and notarization are not completed in this repository state. The local `.app` bundle created by `scripts/build-macos-companion-app` is unsigned.

To prepare a distributable app, a later release must:

1. Create or generate a proper macOS app bundle target.
2. Configure bundle identifier, version, icon, entitlements, and hardened runtime.
3. Sign with an Apple Developer ID certificate.
4. Notarize with Apple notary service.
5. Staple the notarization ticket.
6. Verify Gatekeeper launch on a clean macOS user account.

Do not describe the app as App Store released, signed, notarized, or production-distributed until those steps have actually succeeded.
