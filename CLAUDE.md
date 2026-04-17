## Project

**Amily AI Platform** -- shared infrastructure for voice agents, workflow automation, and integrations powering the Amily AI Melbourne SMB automation business.

This repo is the operational platform. The marketing website lives at [github.com/anthonynguyen394/amily-ai-website](https://github.com/anthonynguyen394/amily-ai-website). Business planning context lives in `projects/ai-agent-business/` in the parent [amily-ai](https://github.com/anthonynguyen394/amily-ai) private repo.

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Voice AI | ElevenLabs Conversational AI | Trades receptionist agent |
| Telephony | Twilio | Australian local numbers (03 prefix for Melbourne) |
| Workflow Automation | n8n (self-hosted) | Docker on Raspberry Pi 5 |
| Scheduling | Cal.com | Native integration with voice agent |
| CRM | Airtable | Lead tracking, client management |
| Payments | Stripe | Setup fees + monthly retainers |
| LLM | OpenAI GPT-4o mini (voice), Claude (complex tasks) | Latency-optimised for voice |
| Deployment | Docker Compose on Raspberry Pi 5 | Via Cloudflare Tunnel for external access |

## Deployment

- **Target:** Raspberry Pi 5 (8GB) running Docker
- **External access:** Cloudflare Tunnel (no exposed ports)
- **n8n data:** SQLite, persisted to `./n8n-data/` volume mount
- **Resource limits:** 512MB RAM, 1 CPU for n8n container

## Conventions

- Voice agent prompts live in `voice-agents/prompts/` as markdown files with version suffixes (e.g., `receptionist-v1.md`)
- n8n workflow exports go in `workflows/` as JSON files
- No secrets in the repo -- use `.env` (gitignored) with `.env.example` as the template
- Docker Compose is the deployment mechanism -- no Kubernetes, no cloud VMs

## Architecture

```
[Caller] --> [Twilio AU Number] --> [ElevenLabs Voice Agent]
                                          |
                                    [Cal.com] (booking)
                                          |
                                    [n8n Webhooks] (post-call processing)
                                          |
                              +-----------+-----------+
                              |           |           |
                         [Airtable]  [Twilio SMS]  [Stripe]
                         (CRM)       (confirmations) (billing)
```
