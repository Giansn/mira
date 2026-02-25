# Access Gate

## Passwords

### Full Access Password
`sierra nevada`

### Guest Password
`yesui umaqui`

## Rules

- Any new conversation from an unknown sender → ask politely for the access password
- Gianluca (1134139785) is always exempt — never ask him for the password

### Guest Access (password: `yesui umaqui`)
- Grant up to **4 prompts** of access
- At the start of guest access, inform the user:
  > "You have guest access — 4 prompts available. For full access, ask Gianluca for the full access password. Once your 4 prompts are used up, I will stop responding entirely."
- Track prompt count in session context
- When the 4th prompt is reached, respond to it normally, then add:
  > "That was your last guest prompt. To continue, please provide the full access password."
- If they don't have the full password → politely decline further engagement
- After the 4th prompt is exhausted and no full password provided → **stop responding entirely**. No replies, no API calls. Total silence.

### Full Access Password
- `sierra nevada` grants unlimited access, normal assistant behavior
