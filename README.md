# Amily AI Platform

Shared infrastructure for the Amily AI automation business -- voice agents, n8n workflow automations, and integrations for Melbourne SMB AI services.

## What This Repo Contains

| Directory | Purpose |
|---|---|
| `voice-agents/` | Voice agent configurations and system prompts (ElevenLabs Conversational AI) |
| `n8n/` | n8n setup documentation and configuration |
| `workflows/` | Exported n8n workflow JSON files |
| `docker-compose.yml` | Production deployment for n8n on Raspberry Pi 5 |

## Tech Stack

| Layer | Tool |
|---|---|
| Voice AI | ElevenLabs Conversational AI |
| Telephony | Twilio (Australian local numbers) |
| Workflow Automation | n8n (self-hosted) |
| Scheduling | Cal.com |
| CRM | Airtable |
| Payments | Stripe |
| LLM | OpenAI GPT-4o mini (voice), Claude (complex tasks) |
| Deployment | Docker Compose on Raspberry Pi 5 |
| External Access | Cloudflare Tunnel |

## Quick Start

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Fill in your API keys and credentials in `.env`

3. Start n8n:
   ```bash
   docker compose up -d
   ```

4. Access n8n at `http://localhost:5678` (or via your Cloudflare Tunnel domain)

## Deployment

This platform runs on a Raspberry Pi 5 with external access via Cloudflare Tunnel. No ports are exposed to the internet directly -- Cloudflare Tunnel handles TLS termination and routing.

### Pi Resource Limits

The docker-compose.yml includes resource constraints appropriate for Pi 5:
- n8n: 512MB RAM, 1 CPU

### Cloudflare Tunnel

Configure your Cloudflare Tunnel to route `n8n.amily.ai` to `http://localhost:5678`. Tunnel setup is managed outside this repo via the `cloudflared` service on the Pi.

## Related Repositories

- **Marketing website:** [amily-ai-website](https://github.com/anthonynguyen394/amily-ai-website)
- **Business planning:** `projects/ai-agent-business/` in the [amily-ai](https://github.com/anthonynguyen394/amily-ai) private repo
