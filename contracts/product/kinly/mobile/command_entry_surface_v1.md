---
Domain: Command
Capability: Mobile Command Entry Surface
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Canonical-Id: mobile_command_entry_surface
Depends-On: contracts/api/kinly/command/command_entry_api_v1.md, contracts/api/kinly/command/command_router_contract_v1_1.md, contracts/api/kinly/command/command_ai_pipeline_v1.md
Relates-To: contracts/product/kinly/shared/voice_grocery_capture_v1.md, contracts/product/kinly/mobile/paywall_gate_product_v1.md
See-Also: contracts/product/kinly/mobile/core_placement_rules_v1.md, contracts/api/kinly/command/voice_command_capture_v1.md
---

# Mobile Command Entry Surface v1

## 1. Purpose

Define the canonical mobile UI entry points for Kinly command input.

This contract answers:

- where command entry lives in the app
- whether text and voice are both first-class inputs
- how a dedicated Kinly widget launches command capture

The command surface is a capture affordance first, not a destination page. It
exists to let the user say or type what they want without navigating through
feature-specific flows first.

## 2. Canonical Entry Points

V1 mobile command entry MUST expose two primary entry points:

1. A docked command composer on the Today page
2. A Kinly-branded widget entry that opens directly into voice capture

Both entry points submit into the same backend command pipeline defined by
`command_entry_api_v1.md`.

## 3. Today Page Command Composer

### 3.1 Presence

The Today page MUST include a persistent command composer near the bottom of the
surface.

The composer MUST include:

- a text input field for typed commands
- a voice trigger icon for audio capture

### 3.2 Placement

Placement rule for v1:

- the command composer MUST sit at the bottom of the Today page
- when the Today surface already contains the primary `+` action, the command
  composer MUST appear below that `+` action rather than replacing it
- the command composer MUST remain visually associated with Today rather than
  appearing as a floating global assistant overlay

Intent of this rule:

- the existing `+` action remains the explicit manual creation affordance
- the command composer becomes the low-friction natural-language affordance
- users can discover both without ambiguity

### 3.3 Interaction

Text path:

- user taps the text field
- keyboard opens
- user may submit a free-form command such as "remind me to pay rent tomorrow"

Voice path:

- user taps the voice icon
- app opens the voice recording state immediately
- the app MUST make it clear that the user is now recording, listening, or
  transcribing

The user MUST NOT be forced through an extra mode-picker dialog when they have
already chosen text or voice from the composer.

### 3.4 Empty State and Hinting

The text field SHOULD use helper copy that teaches open-ended command behavior,
for example:

- "Ask Kinly to add, remind, split, or open something"

The voice icon MUST read as a command capture affordance, not as a call,
message, or search affordance.

## 4. Widget Entry

### 4.1 Widget Semantics

V1 MAY provide a mobile widget that displays the Kinly logo as the primary tap
target.

If the widget is present, tapping the Kinly logo MUST:

- launch the app into the authenticated home context when possible
- open the command surface directly in voice capture mode
- bypass the text-first composer state

The widget interaction is explicitly voice-first. It exists for "capture it
now" behavior when the user is outside the app.

### 4.2 Widget Outcome

After the widget tap:

- recording starts immediately or the recording-ready screen appears with the
  microphone armed
- the user SHOULD need at most one additional tap to begin speaking if OS
  permission or foreground constraints prevent instant recording
- after transcription, the flow rejoins the same command result handling used by
  the Today composer

### 4.3 Permission Handling

If microphone permission is missing or blocked:

- the app MUST interrupt with the platform permission flow or a clear recovery
  screen
- the app MUST preserve the widget's voice-first intent
- the app MUST NOT silently dump the user into an unrelated page

## 5. Shared UX Rules

The following rules apply to both entry points:

- text and voice MUST resolve through the same command runtime and result model
- `input_mode` MUST be sent as `text` or `voice` exactly as defined in the API
  contracts
- users MUST be able to review the transcript or typed text before an unsafe
  action is executed
- quota or paywall blocks MUST use the standard command paywall handling defined
  in `paywall_gate_product_v1.md`
- failed transcription MUST fall back to editable text rather than ending the
  flow

## 6. Voice Recording State Model

The mobile voice UI MUST expose a simple state model that matches the backend
voice capture lifecycle without leaking backend implementation detail.

Canonical visible states for v1:

1. `idle`
2. `listening`
3. `finishing`
4. `transcribing`
5. `review`
6. `submitting`
7. `error`

State meanings:

- `idle`: no active capture session
- `listening`: microphone is active and the app is capturing speech
- `finishing`: recording has stopped and audio is being finalized locally
- `transcribing`: speech is being converted into text
- `review`: transcript is editable and ready for user inspection or submission
- `submitting`: transcript has been accepted and is being sent into the command
  runtime
- `error`: capture or transcription could not continue without user recovery

The UI MUST clearly distinguish:

- active recording from background processing
- transcription from command processing
- recoverable errors from completed submissions

## 7. Recording Controls

The voice surface MUST provide explicit user control over recording.

Required controls:

- start recording
- stop recording
- cancel current recording

V1 MAY support either tap-to-record or press-and-hold, but the chosen pattern
MUST still expose a clear manual stop affordance.

Rules:

- once recording has started, the active state MUST be visually obvious
- users MUST be able to stop recording before automatic silence detection ends
  the turn
- cancelling a recording MUST discard the unfinished audio payload and return to
  `idle` or the text composer without submitting anything

## 8. Transcript Review And Editing

Voice input MUST converge to editable text before unsafe execution.

Transcript rules:

- after transcription, the app MUST show the recognized text in an editable
  review state
- the user MUST be able to correct the transcript before submission
- editing the transcript converts the interaction into a text-reviewed command,
  but the original submission MAY still be tagged with `input_mode = "voice"`
  because the capture origin was voice
- the app MUST allow the user to resubmit the corrected transcript without
  recording again

Recommended review actions:

- `Send`
- `Edit`
- `Retry voice`
- `Cancel`

When the backend result is a low-risk `execute`, the client MAY submit
immediately after transcription for speed, but only when the interaction does
not require confirmation and the user still has a visible path to undo or amend
the result afterward.

When the backend result is `confirm`, `inline`, `route`, or `unknown`, the
transcript or typed command text MUST remain inspectable to preserve trust and
debuggability.

## 9. Widget Launch And Permission Behavior

The widget flow is stricter than the in-app composer because the user has
already signaled voice intent before the app is foregrounded.

### 9.1 Happy Path

On widget tap:

- app opens directly into the command voice surface
- app enters `listening` immediately when platform constraints allow
- otherwise the app opens into a recording-ready screen that preserves the
  widget-origin context and asks for at most one additional user action

### 9.2 Permission Not Yet Granted

If microphone permission has not yet been granted:

- the app MUST request microphone permission immediately in the widget-started
  flow
- if the OS requires a pre-permission explanation screen, that screen MUST be
  specific to voice capture and MUST offer a direct path to continue
- after permission is granted, the app SHOULD resume directly into recording
  rather than falling back to Today

### 9.3 Permission Denied Or Blocked

If permission is denied, restricted, or permanently blocked:

- the app MUST show a dedicated recovery state
- the recovery state MUST explain that voice capture needs microphone access
- the recovery state MUST offer:
  - a path to open system settings when the platform requires it
  - a fallback path into the text command composer
- the app MUST preserve the fact that the entry originated from the widget for
  analytics and debugging

### 9.4 Locked Or Unauthenticated Cases

If the app cannot immediately enter an authenticated home context:

- the app MAY require unlock, auth, or home restoration first
- once that gate is passed, the app SHOULD return to the widget-started command
  flow rather than dropping intent
- if voice capture cannot resume, the app MUST fall back to the command composer
  rather than a generic home screen landing

## 10. Error And Recovery Rules

The voice command surface MUST treat capture failures as recoverable.

Required recovery cases:

- transcription timeout
- empty or unusable transcript
- microphone permission denied
- audio capture interrupted by OS, phone call, or app backgrounding

Recovery rules:

- `transcription_timeout` MUST show any partial transcript that is safe to
  expose and let the user edit or retry
- an empty transcript MUST not be auto-submitted
- interruptions SHOULD preserve the partial transcript when available
- retrying voice capture SHOULD create a new capture attempt without destroying
  stable reviewed text the user has already edited manually

## 11. Analytics And Attribution

The mobile client SHOULD distinguish command-entry origin for analysis and
product tuning.

At minimum, analytics SHOULD capture:

- entry origin: `today_composer_text`, `today_composer_voice`, or
  `widget_voice`
- whether the user edited the transcript before submission
- whether microphone permission blocked first-run capture
- whether the flow recovered via text fallback

These signals are product telemetry only. They MUST NOT change the canonical
backend command contract.

## 12. Non-Goals

V1 does not require:

- a standalone command tab
- a chat history screen
- a persistent floating assistant bubble across all app screens
- widget-driven text entry
- continuous streaming partial-transcript command execution
- background passive listening

## 13. Product Invariant

Kinly command entry on mobile is dual-mode:

- on Today, users get a text field plus voice icon below the existing `+`
  action
- from the Kinly widget, users jump straight into audio capture

Users can always recover from voice into editable text, and widget-origin voice
intent must remain voice-first unless the user explicitly chooses the text
fallback.
