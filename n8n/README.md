# n8n Setup

Self-hosted n8n instance for Amily AI workflow automation, running on Raspberry Pi 5 via Docker Compose.

## Quick Start

From the repo root:

```bash
cp .env.example .env
# Edit .env with your credentials
docker compose up -d
```

Access at `http://localhost:5678` (local) or `https://n8n.amily.ai` (via Cloudflare Tunnel).

## Configuration

| Variable | Purpose |
|---|---|
| `N8N_HOST` | Hostname for n8n (default: `n8n.amily.ai`) |
| `N8N_PORT` | Internal port (default: `5678`) |
| `N8N_PROTOCOL` | Protocol for webhook URLs (default: `https`) |
| `WEBHOOK_URL` | Full webhook base URL |
| `GENERIC_TIMEZONE` | Timezone for scheduling (default: `Australia/Melbourne`) |
| `N8N_BASIC_AUTH_USER` | Basic auth username |
| `N8N_BASIC_AUTH_PASSWORD` | Basic auth password |

## Data Persistence

- Database: SQLite at `./n8n-data/database.sqlite`
- Credentials and workflow data are stored in the SQLite database
- The `n8n-data/` directory is gitignored -- back up separately

## Workflows

Exported workflow JSON files are stored in `../workflows/`. Import them via the n8n UI or API.

## Planned Workflows

- **Post-call processing:** Receive webhook from ElevenLabs after call, classify intent, update Airtable, send SMS confirmation
- **Review request:** Trigger SMS review request after job completion, monitor Google Business Profile for responses
- **Client onboarding:** Intake form triggers CRM setup, welcome email, and kickoff scheduling
