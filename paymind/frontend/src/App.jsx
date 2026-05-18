import React, { useState, useRef } from 'react';
import { Play, CheckCircle, Clock, FileText, Coins, Link2, Hash, AlertCircle, Loader2, Trash2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '');

const STEPS = [
  { id: 'executing', label: 'Executing Task', description: 'Running your task through the LLM via OpenRouter', icon: Play },
  { id: 'invoicing', label: 'Generating Invoice', description: 'Calculating cost from token usage', icon: FileText },
  { id: 'paying', label: 'Settling Payment', description: 'Sending payment on Kite chain', icon: Coins },
  { id: 'attesting', label: 'On-chain Attestation', description: 'Writing proof of work to Kite chain', icon: Hash },
];

function StepIndicator({ step, status }) {
  const Icon = step.icon;
  const isActive = status === 'active';
  const isDone = status === 'completed';
  const isError = status === 'error';

  return (
    <div className={`flex items-center gap-4 p-4 rounded-xl border-2 transition-all duration-500 ${
      isActive  ? 'bg-purple-600/20 border-purple-500 scale-[1.01]'
      : isDone  ? 'bg-green-900/20 border-green-600'
      : isError ? 'bg-red-900/20 border-red-600'
      :           'bg-slate-800/40 border-slate-700'
    }`}>
      <div className={`p-2 rounded-full flex-shrink-0 ${
        isActive  ? 'bg-purple-500'
        : isDone  ? 'bg-green-600'
        : isError ? 'bg-red-600'
        :           'bg-slate-700'
      }`}>
        {isActive ? <Loader2 size={22} className="text-white animate-spin" />
         : isDone  ? <CheckCircle size={22} className="text-white" />
         : isError ? <AlertCircle size={22} className="text-white" />
         :           <Icon size={22} className="text-slate-400" />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-white">{step.label}</p>
        <p className={`text-xs truncate ${isActive ? 'text-purple-300' : isDone ? 'text-green-400' : 'text-slate-500'}`}>
          {isActive ? 'In progress...' : isDone ? 'Completed' : isError ? 'Failed' : step.description}
        </p>
      </div>
      <span className={`text-xs font-bold ${isActive ? 'text-purple-400' : isDone ? 'text-green-400' : isError ? 'text-red-400' : 'text-slate-600'}`}>
        {isDone ? '✓' : isActive ? '●' : isError ? '✗' : '○'}
      </span>
    </div>
  );
}

function App() {
  const [task, setTask]               = useState('');
  const [wallet, setWallet]           = useState('');
  const [loading, setLoading]         = useState(false);
  const [activeStep, setActiveStep]   = useState('');
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [result, setResult]           = useState(null);
  const [error, setError]             = useState(null);
  const esRef = useRef(null);

  const getStepStatus = (stepId) => {
    if (activeStep === 'error' && stepId === activeStep) return 'error';
    if (completedSteps.has(stepId))      return 'completed';
    if (stepId === activeStep)           return 'active';
    return 'pending';
  };

  const runAgent = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveStep('executing');
    setCompletedSteps(new Set());

    try {
      const response = await fetch(`${API_BASE_URL}/run-agent-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, wallet_address: wallet }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail?.error || err.detail || 'Request failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop();

        for (const part of parts) {
          const eventLine = part.split('\n').find(l => l.startsWith('event:'));
          const dataLine  = part.split('\n').find(l => l.startsWith('data:'));
          if (!eventLine || !dataLine) continue;

          const eventType = eventLine.replace('event:', '').trim();
          const data      = JSON.parse(dataLine.replace('data:', '').trim());

          if (eventType === 'status') {
            const prev = STEPS[STEPS.findIndex(s => s.id === data.step) - 1];
            if (prev) setCompletedSteps(s => new Set([...s, prev.id]));
            setActiveStep(data.step);
          } else if (eventType === 'complete') {
            setCompletedSteps(new Set(STEPS.map(s => s.id)));
            setActiveStep('completed');
            setResult(data);
          } else if (eventType === 'error') {
            setActiveStep('error');
            setError(`Step "${data.step}" failed: ${data.message}`);
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setActiveStep('error');
    } finally {
      setLoading(false);
    }
  };

  const explorerUrl = (hash) => `https://testnet.kitescan.ai/tx/${hash}`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-slate-900">
      <div className="container mx-auto px-4 py-12 max-w-4xl">

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-extrabold text-white mb-3 tracking-tight">
            Pay<span className="text-purple-400">Mind</span>
          </h1>
          <p className="text-lg text-purple-200">Autonomous AI Agent · Kite AI Hackathon 2026</p>
          <p className="text-sm text-slate-400 mt-1">Execute · Invoice · Pay · Attest zero human involvement</p>
        </div>

        {/* Form */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20 mb-8">
          <form onSubmit={runAgent} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-purple-200 mb-2">Task Description</label>
              <textarea
                value={task}
                onChange={e => setTask(e.target.value)}
                placeholder="Describe the task for the AI agent… (e.g. 'Write a blog post about DeFi')"
                rows={4}
                className="w-full px-4 py-3 bg-slate-900/80 border border-purple-500/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                required disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-purple-200 mb-2">Wallet Address (Kite Chain)</label>
              <input
                type="text"
                value={wallet}
                onChange={e => setWallet(e.target.value)}
                placeholder="0x..."
                className="w-full px-4 py-3 bg-slate-900/80 border border-purple-500/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                required disabled={loading}
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading || !task.trim() || !wallet.trim()}
                className="flex-1 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold text-lg rounded-xl shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] flex items-center justify-center gap-2"
              >
                {loading
                  ? <><Loader2 size={20} className="animate-spin" /> Agent running…</>
                  : <><Play size={20} /> Run Agent</>}
              </button>
              <button
                type="button"
                onClick={() => {
                  setTask('');
                  setWallet('');
                  setResult(null);
                  setError(null);
                  setActiveStep('');
                  setCompletedSteps(new Set());
                }}
                disabled={loading}
                className="px-5 py-4 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] flex items-center justify-center gap-2"
              >
                <Trash2 size={18} /> Clear
              </button>
            </div>
          </form>
        </div>

        {/* Live Steps */}
        {(loading || activeStep === 'completed' || activeStep === 'error') && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20 mb-8">
            <h3 className="text-lg font-bold text-white mb-5 flex items-center gap-2">
              <Clock size={20} className="text-purple-400" /> Agent Pipeline
            </h3>
            <div className="space-y-3">
              {STEPS.map(step => (
                <StepIndicator key={step.id} step={step} status={getStepStatus(step.id)} />
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/40 rounded-2xl p-6 border border-red-500/30 mb-8 flex items-start gap-3">
            <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="font-semibold text-red-300 mb-1">Agent Error</p>
              <p className="text-red-200 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="space-y-6">
            {/* Output */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/20">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <CheckCircle className="text-green-400" size={20} /> Agent Output
              </h3>
              <pre className="bg-slate-900/80 rounded-xl p-4 text-slate-200 text-sm whitespace-pre-wrap leading-relaxed border border-purple-500/10">
                {result.output}
              </pre>
            </div>

            {/* Invoice */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/20">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <FileText className="text-purple-400" size={20} /> Invoice
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: 'Prompt Tokens',     value: result.invoice.prompt_tokens?.toLocaleString()     ?? '—' },
                  { label: 'Completion Tokens',  value: result.invoice.completion_tokens?.toLocaleString() ?? '—' },
                  { label: 'Total Tokens',       value: result.invoice.total_tokens?.toLocaleString()      ?? '—' },
                  { label: 'Cost (USD)',          value: `$${(result.invoice.cost_usd || 0).toFixed(6)}`, green: true },
                ].map(({ label, value, green }) => (
                  <div key={label} className="bg-slate-900/80 rounded-xl p-4 border border-purple-500/10">
                    <p className="text-xs text-purple-300 mb-1">{label}</p>
                    <p className={`text-xl font-bold ${green ? 'text-green-400' : 'text-white'}`}>{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Transactions */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/20">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Link2 className="text-blue-400" size={20} /> Kite Chain Transactions
              </h3>
              <div className="space-y-4">
                <div className="bg-slate-900/80 rounded-xl p-4 border border-purple-500/10">
                  <p className="text-xs text-purple-300 mb-2 font-medium">Payment Transaction</p>
                  <a
                    href={explorerUrl(result.tx_hash)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 font-mono text-sm break-all flex items-center gap-2 transition-colors"
                  >
                    {result.tx_hash} <Link2 size={12} />
                  </a>
                </div>
                <div className="bg-slate-900/80 rounded-xl p-4 border border-purple-500/10">
                  <p className="text-xs text-purple-300 mb-2 font-medium">Attestation Hash</p>
                  <div className="flex items-start gap-2">
                    <Hash size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                    <span className="text-green-300 font-mono text-sm break-all">{result.attestation_hash}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <p className="text-center mt-12 text-slate-500 text-xs">
          Powered by PayMind · Kite AI Global Hackathon 2026
        </p>
      </div>
    </div>
  );
}

export default App;
