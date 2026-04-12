# PayMind

> Autonomous AI agent that executes tasks, self-generates invoices, and settles payments on Kite chain with on-chain attestations. Zero human involvement.

Built for the **Kite AI Global Hackathon 2026** — Novel Track.

---

## What is PayMind?

PayMind is a fully autonomous AI agent that:

1. **Receives a task** from a user (e.g. "Write a blog post about Web3")
2. **Executes the task** using an LLM via OpenRouter
3. **Auto-generates an invoice** based on task complexity & token usage
4. **Settles payment on Kite chain** — no human approval needed
5. **Posts an on-chain attestation** as proof of work + payment receipt
6. **Displays everything** in a live React dashboard — logs, output, tx hash, attestation

---

## Architecture

```
User Input
    │
    ▼
LangGraph Agent (Orchestrator)
    ├── Task Execution Node  →  OpenRouter (LLM)
    ├── Invoice Generator Node  →  Calculates cost
    ├── Payment Node  →  Kite Chain SDK
    └── Attestation Node  →  Kite Chain (on-chain proof)
         │
         ▼
    FastAPI Backend
         │
         ▼
    React Frontend (Live Dashboard)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | Python + LangGraph |
| LLM Access | OpenRouter (multi-model) |
| Backend API | FastAPI |
| Frontend | React + TailwindCSS |
| Blockchain | Kite Chain SDK |
| Deployment | Vercel (frontend) + Railway (backend) |

---

## Project Structure

```
paymind/
├── backend/
│   ├── agent/
│   │   ├── graph.py          # LangGraph agent definition
│   │   ├── nodes.py          # Task, invoice, payment, attestation nodes
│   │   └── state.py          # Agent state schema
│   ├── api/
│   │   └── main.py           # FastAPI routes
│   ├── kite/
│   │   └── client.py         # Kite chain SDK integration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # UI components
│   │   └── App.jsx           # Main dashboard
│   └── package.json
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Kite Chain wallet + API key
- OpenRouter API key

### Backend

```bash
cd backend
pip install -r requirements.txt

cp .env.example .env
# Fill in your API keys in .env

uvicorn api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

```env
OPENROUTER_API_KEY=your_openrouter_key
KITE_RPC_URL=https://rpc.kite.ai
KITE_PRIVATE_KEY=your_wallet_private_key
KITE_CONTRACT_ADDRESS=your_contract_address
```

---

## How It Works (End-to-End)

1. User submits a task via the web UI
2. LangGraph orchestrates the agent pipeline
3. OpenRouter calls the best available LLM to complete the task
4. Invoice is auto-generated based on token usage + complexity score
5. Payment is sent on Kite chain from user wallet to agent wallet
6. Attestation is posted on-chain as tamper-proof record
7. Frontend displays the result, invoice, tx hash, and attestation link

---

## Hackathon Track

**Novel Track** — PayMind introduces the concept of a *self-billing autonomous agent* — an agent that not only does the work but handles its own compensation and proof of work on-chain. This unlocks a new primitive: the **autonomous freelancer economy**.

---

## Judging Criteria Coverage

| Criteria | How PayMind addresses it |
|---|---|
| Agent Autonomy | Fully autonomous pipeline — no human in the loop |
| Real-World Applicability | Freelancer payments, API billing, agent-to-agent economy |
| Developer Experience | Clean README, live demo, modular codebase |
| Novel / Creativity | First self-billing agent on Kite chain |

---

## Live Demo

> Coming soon — will be deployed on Vercel + Railway

---

## Team

Built with for the Kite AI Global Hackathon 2026.

---

## License

MIT