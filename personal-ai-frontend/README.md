# Personal AI — Frontend

Conversational interface for the Personal AI platform. Features voice recognition, digital avatar, and real-time dashboards connected to a Python backend with PostgreSQL.

## Stack

- **Framework:** React 19 + TanStack Start (SPA)
- **Routing:** TanStack Router
- **Styling:** Tailwind CSS v4 + shadcn/ui
- **Animation:** Framer Motion
- **Avatar:** Simli (digital avatar with audio streaming)
- **Voice:** Web Speech API (recognition) + OpenAI TTS (synthesis)
- **Build:** Vite + Cloudflare Workers (deploy)
- **Backend:** FastAPI + PostgreSQL (via Docker Compose)

## Structure

```
src/
  routes/
    __root.tsx      # Root layout, SEO, 404
    index.tsx       # Main page (orb, input, microphone, response)
    panel.tsx       # Detachable panel with auto-refresh (30s/1min/5min)
  components/
    personal-ai/
      Orb.tsx              # Animated orb (4 states: idle, listening, processing, speaking)
      InputPill.tsx        # Styled input with microphone
      ResponseRenderer.tsx # Renders all workflow responses
      ResponseSheet.tsx    # Animated sheet for displaying responses
      AvatarStream.tsx     # Audio/video streaming for Simli avatar
      HelpModal.tsx        # Modal with example queries
    ui/                    # shadcn/ui components
  lib/
    personal-ai-workflows.ts  # Workflow mapping (URL, buildBody, transformResponse)
    voice-ai.ts               # TTS pipeline (OpenAI → audio → Simli)
    utils.ts                  # Utilities (cn)
  hooks/
    use-speech-recognition.ts # Web Speech API hook
    use-mobile.tsx            # Mobile detection
  styles.css               # Theme with oklch variables
```

## Workflows

| Tag    | Feature               | Backend               | Description                           |
|--------|-----------------------|-----------------------|---------------------------------------|
| WF-16  | Voice dashboard       | `POST /dashboard`     | Status, risks, bottlenecks, etc       |
| WF-12  | Conversational copilot| `POST /chat`          | Questions about hospital data         |
| WF-07  | Clinical documentation| `POST /workflow`      | Generate progress notes               |
| WF-08  | Regulatory copilot    | `POST /workflow`      | Authorization justifications          |

Workflow detection is automatic based on keywords in the user's input.

## Quick Start (Docker)

The frontend is included in the Docker Compose setup alongside the backend and PostgreSQL:

```bash
cd personal-ai-backend
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d
```

Access the frontend at **http://localhost:3000**.

## Local Development

```bash
cd personal-ai-frontend

# Copy and edit .env
VITE_API_BASE_URL=http://localhost:8000
VITE_SIMLI_API_KEY=...
VITE_SIMLI_FACE_ID=...
VITE_OPENAI_API_KEY=...

npm install
npm run dev
```

## Scripts

| Command            | Description                    |
|--------------------|--------------------------------|
| `npm run dev`      | Dev server with HMR            |
| `npm run build`    | Production build (client+SSR)  |
| `npm run preview`  | Preview the build              |
| `npm run lint`     | ESLint                         |
| `npm run format`   | Prettier                       |

## Notes

- The frontend expects the backend at `VITE_API_BASE_URL` (default: `http://localhost:8000`).
- Simli avatar requires valid `VITE_SIMLI_API_KEY` and `VITE_SIMLI_FACE_ID`.
- Deployment uses Cloudflare Workers (config in `wrangler.jsonc`).
