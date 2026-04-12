# PayMind

> Autonomous AI Agent for Kite AI Global Hackathon 2026

PayMind is an end-to-end autonomous AI agent system that receives a task, executes it using an LLM via OpenRouter, auto-generates an invoice based on token usage, settles payment on Kite chain, and posts an on-chain attestation as proof — with zero human involvement.

## Architecture

```
┌─────────────────┐
│   User Request  │
│  {task, wallet} │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│           FastAPI Backend (Python)          │
│  ┌──────────────────────────────────────┐  │
│  │      LangGraph Agent Workflow        │  │
│  │  execute_task → generate_invoice     │  │
│  │  → settle_payment → post_attestation│  │
│  └──────────────────────────────────────┘  │
└─────────────────┬─────────────────────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐
│OpenRouter│ │  Kite    │ │  Kite Chain  │
│   API   │ │  Chain   │ │  (EVM)       │
└─────────┘ └──────────┘ └──────────────┘
```

## Project Structure

```
paymind/
├── backend/
│   ├── agent/
│   │   ├── state.py      # TypedDict state schema
│   │   ├── nodes.py      # 4 async workflow nodes
│   │   └── graph.py      # LangGraph StateGraph
│   ├── api/
│   │   └── main.py       # FastAPI application
│   ├── kite/
│   │   └── client.py     # Kite chain SDK integration
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/   # (reserved for future components)
│   │   ├── App.jsx       # Main dashboard
│   │   └── main.jsx      # React entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

## Features

- **Task Execution**: Asynchronously execute tasks using OpenRouter LLM APIs
- **Automatic Invoicing**: Generate invoices based on actual token usage with cost calculation
- **Smart Payments**: Automatically settle payments on Kite chain via web3.py
- **On-Chain Attestation**: Post cryptographic proof of completion on-chain
- **Live Dashboard**: React frontend with real-time step tracking and transaction details
- **Production-Ready**: Error handling, CORS, environment configuration

## Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI** - Modern web framework
- **LangGraph** - Stateful agent workflow orchestration
- **LangChain** - LLM orchestration
- **web3.py** - Ethereum/Kite chain interaction
- **httpx** - Async HTTP client

### Frontend
- **React 18** - UI library
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Vite** - Build tool

### Blockchain
- **Kite Chain** - EVM-compatible blockchain
- **web3.py** - Python Web3 library

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Kite chain RPC endpoint
- OpenRouter API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd paymind/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your actual values
```

5. Run the API server:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API endpoints:
- `GET /` - API info
- `GET /health` - Health check
- `POST /run-agent` - Execute agent workflow

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd paymind/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment (optional):
Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

The dashboard will be available at: `http://localhost:5173`

## Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access | Yes |
| `OPENROUTER_MODEL` | Model ID (default: `anthropic/claude-3.5-sonnet`) | No |
| `KITE_RPC_URL` | Kite chain RPC endpoint | Yes |
| `KITE_PRIVATE_KEY` | Private key for signing transactions | Yes |
| `KITE_CONTRACT_ADDRESS` | Smart contract address for payments/attestations | Yes |
| `PAYMENT_RECIPIENT_ADDRESS` | Wallet address to receive payments | Yes |

### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## API Usage

### Run Agent

**Request:**
```json
POST /run-agent
{
  "task": "Analyze this data and write a summary",
  "wallet_address": "0x..."
}
```

**Response:**
```json
{
  "session_id": "abc12345",
  "output": "Here's your analysis...",
  "invoice": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300,
    "cost_usd": 0.003,
    "amount_wei": "3000000000000000"
  },
  "tx_hash": "0x...",
  "attestation_hash": "0x...",
  "status": "completed"
}
```

## Agent Workflow

1. **Execute Task**: Agent sends task to OpenRouter, receives completion with token usage
2. **Generate Invoice**: Calculates cost based on token usage (configurable rate)
3. **Settle Payment**: Transfers payment amount to recipient on Kite chain
4. **Post Attestation**: Records cryptographic proof of completion on-chain

### Status Values

- `executing` - Task is being processed by LLM
- `invoicing` - Invoice is being generated
- `paying` - Payment transaction in progress
- `attesting` - Attestation being posted
- `completed` - Workflow finished successfully
- `error` - An error occurred (check error details)

## Deployment

### Backend (Railway)

1. Connect your repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy from `paymind/backend` directory
4. Railway auto-detects Python and runs with `uvicorn`

### Frontend (Vercel)

1. Import project to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Configure environment variable `VITE_API_URL` with your deployed backend URL
5. Deploy from `paymind/frontend` directory

## Development Notes

- The agent workflow uses LangGraph's StateGraph for deterministic state transitions
- All nodes are async for optimal performance
- Error handling is implemented at each stage with partial state rollback
- Transaction receipts are waited for synchronously (can be made async for production)
- The Kite client uses a minimal ABI; in production, load from compiled contract JSON

## Security Considerations

**For production use:**

- Use environment variable validation libraries (e.g., pydantic-settings)
- Implement rate limiting on API endpoints
- Add authentication/authorization middleware
- Validate wallet address format rigorously
- Implement retry logic with exponential backoff for blockchain transactions
- Store private keys in secure vault (not environment variables)
- Use HTTPS in production and set proper CORS origins
- Implement request logging and monitoring
- Add request timeouts and circuit breakers
- Consider using Web3 providers with better reliability

## License

MIT

## Acknowledgments

- [Kite AI](https://kite.ai) - for the hackathon opportunity
- [OpenRouter](https://openrouter.ai) - for unified LLM API access
- [LangChain](https://langchain.com) & [LangGraph](https://langgraph.com) - for agent orchestration
- [FastAPI](https://fastapi.tiangolo.com) - for the API framework
- [TailwindCSS](https://tailwindcss.com) - for styling

---

Built for Kite AI Global Hackathon 2026.
