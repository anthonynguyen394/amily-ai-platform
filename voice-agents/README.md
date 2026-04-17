# Voice Agents

Voice agent configurations for ElevenLabs Conversational AI.

## Agents

| Agent | Prompt | Purpose |
|---|---|---|
| Trades Receptionist | `prompts/receptionist-v1.md` | AI receptionist for Melbourne trades businesses |

## Platform

- **Provider:** ElevenLabs Conversational AI
- **Telephony:** Twilio (Australian local numbers, 03 prefix for Melbourne)
- **Scheduling:** Cal.com (native integration)
- **LLM:** OpenAI GPT-4o mini (low latency for voice)

## Prompt Versioning

Prompts are versioned with suffixes (e.g., `receptionist-v1.md`, `receptionist-v2.md`). When updating a prompt:

1. Create a new version file (don't overwrite the old one)
2. Test the new version with test calls
3. Update the ElevenLabs agent to use the new prompt
4. Document what changed and why in the commit message
