# Salux Health AI — Frontend

Interface conversacional do hospital Salux. Reconhecimento de voz, avatar digital e dashboards em tempo real.

## Stack

- **Framework:** React 19 + TanStack Start (SPA)
- **Roteamento:** TanStack Router
- **Estilos:** Tailwind CSS v4 + shadcn/ui
- **Animação:** Framer Motion
- **Avatar:** Simli (digital avatar com áudio streaming)
- **Voz:** Web Speech API (reconhecimento) + OpenAI TTS (síntese)
- **Build:** Vite + Cloudflare Workers (deploy)

## Estrutura

```
src/
  routes/
    __root.tsx      # Layout raiz, SEO, 404
    index.tsx       # Página principal (orb, input, microfone, resposta)
    panel.tsx       # Painel destacável com auto-refresh (30s/1min/5min)
  components/
    salux/
      Orb.tsx              # Orb animada (4 estados: idle, listening, processing, speaking)
      InputPill.tsx        # Input estilizado com microfone
      ResponseRenderer.tsx # Renderiza respostas de todos os workflows
      ResponseSheet.tsx    # Sheet animada para exibir respostas
      AvatarStream.tsx     # Streaming de áudio/vídeo para avatar Simli
      HelpModal.tsx        # Modal com queries de exemplo
    ui/                    # 46 componentes shadcn/ui
  lib/
    salux-workflows.ts     # Mapeamento dos 4 workflows (URL, buildBody, transformResponse)
    voice-ai.ts            # Pipeline TTS (OpenAI → áudio → Simli)
    utils.ts               # Utilitários (cn)
  hooks/
    use-speech-recognition.ts # Web Speech API
    use-mobile.tsx             # Detecção mobile
  styles.css               # Tema Salux com variáveis oklch
```

## Workflows

| Tag    | Front-end              | Backend               | Descrição                     |
|--------|------------------------|-----------------------|-------------------------------|
| WF-16  | Dashboard por voz      | `POST /dashboard`     | Status, riscos, gargalos etc  |
| WF-12  | Copiloto conversacional| `POST /chat`          | Perguntas sobre dados do hospital |
| WF-07  | Documentação clínica   | `POST /workflow`      | Geração de textos de evolução |
| WF-08  | Copiloto regulatório   | `POST /workflow`      | Justificativas para autorização |

A detecção do workflow é automática por palavras-chave no texto do usuário.

## Setup

```bash
cd salux-ai-frontend

# Crie ou edite .env
VITE_API_BASE_URL=http://localhost:8000
VITE_SIMLI_API_KEY=...
VITE_SIMLI_FACE_ID=...
VITE_OPENAI_API_KEY=...

# Instale dependências
npm install

# Inicie dev server
npm run dev
```

## Scripts

| Comando           | Descrição                     |
|-------------------|-------------------------------|
| `npm run dev`     | Dev server com HMR            |
| `npm run build`   | Build produção (client + SSR) |
| `npm run preview` | Preview do build              |
| `npm run lint`    | ESLint                        |
| `npm run format`  | Prettier                      |

## Observações

- O frontend espera o backend rodando em `VITE_API_BASE_URL` (default `http://localhost:8000`).
- O avatar Simli requer `VITE_SIMLI_API_KEY` e `VITE_SIMLI_FACE_ID` válidos.
- O deploy usa Cloudflare Workers (config em `wrangler.jsonc`).
