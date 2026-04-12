import React, { useState } from 'react';
import axios from 'axios';
import { Play, CheckCircle, Clock, FileText, Coins, Link2, Hash } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const STEPS = [
  { id: 'executing', label: 'Executing', icon: Play },
  { id: 'invoicing', label: 'Invoicing', icon: FileText },
  { id: 'paying', label: 'Paying', icon: Coins },
  { id: 'attesting', label: 'Attesting', icon: Hash },
];

function App() {
  const [task, setTask] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runAgent = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setCurrentStep('executing');

    try {
      const response = await axios.post(`${API_BASE_URL}/run-agent`, {
        task,
        wallet_address: walletAddress,
      });

      setResult(response.data);
      setCurrentStep('completed');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      setCurrentStep('error');
    } finally {
      setLoading(false);
    }
  };

  const getStepStatus = (stepId) => {
    if (currentStep === 'error' || currentStep === '') return 'pending';
    const stepOrder = STEPS.map(s => s.id);
    const currentIndex = stepOrder.indexOf(currentStep);
    const stepIndex = stepOrder.indexOf(stepId);

    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getExplorerUrl = (txHash) => {
    // Kite chain explorer URL - adjust based on actual explorer
    return `https://explorer.kite.ai/tx/${txHash}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            PayMind
          </h1>
          <p className="text-xl text-purple-200">
            Autonomous AI Agent for Kite AI Hackathon 2026
          </p>
          <p className="text-sm text-purple-300 mt-2">
            Execute tasks · Generate invoices · Settle payments · On-chain attestation
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20 mb-8">
          <form onSubmit={runAgent} className="space-y-6">
            <div>
              <label htmlFor="task" className="block text-sm font-semibold text-purple-200 mb-2">
                Task Description
              </label>
              <textarea
                id="task"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Describe your task... (e.g., 'Analyze this dataset and generate insights')"
                className="w-full h-32 px-4 py-3 bg-slate-900/80 border border-purple-500/30 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="wallet" className="block text-sm font-semibold text-purple-200 mb-2">
                Wallet Address (Kite Chain)
              </label>
              <input
                id="wallet"
                type="text"
                value={walletAddress}
                onChange={(e) => setWalletAddress(e.target.value)}
                placeholder="0x..."
                className="w-full px-4 py-3 bg-slate-900/80 border border-purple-500/30 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !task.trim() || !walletAddress.trim()}
              className="w-full py-4 px-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold text-lg rounded-lg shadow-lg transform transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Clock className="animate-pulse" size={20} />
                  Running Agent...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Play size={20} />
                  Run Agent
                </span>
              )}
            </button>
          </form>
        </div>

        {/* Progress Steps */}
        {loading && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20 mb-8">
            <h3 className="text-xl font-bold text-white mb-6">Agent Progress</h3>
            <div className="space-y-4">
              {STEPS.map((step, index) => {
                const Icon = step.icon;
                const status = getStepStatus(step.id);
                return (
                  <div
                    key={step.id}
                    className={`flex items-center gap-4 p-4 rounded-lg transition-all duration-300 ${
                      status === 'active'
                        ? 'bg-purple-600/30 border-2 border-purple-500'
                        : status === 'completed'
                        ? 'bg-green-900/30 border-2 border-green-600'
                        : 'bg-slate-700/30 border-2 border-slate-600'
                    }`}
                  >
                    <div
                      className={`p-2 rounded-full ${
                        status === 'active'
                          ? 'bg-purple-500 animate-pulse'
                          : status === 'completed'
                          ? 'bg-green-600'
                          : 'bg-slate-600'
                      }`}
                    >
                      {status === 'completed' ? (
                        <CheckCircle size={24} className="text-white" />
                      ) : (
                        <Icon size={24} className="text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-white">{step.label}</p>
                      {status === 'active' && (
                        <p className="text-sm text-purple-300">In progress...</p>
                      )}
                    </div>
                    <div
                      className={`text-sm font-bold ${
                        status === 'active'
                          ? 'text-purple-300'
                          : status === 'completed'
                          ? 'text-green-400'
                          : 'text-slate-500'
                      }`}
                    >
                      {status === 'completed' ? '✓ Done' : status === 'active' ? '●' : '○'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="space-y-6">
            {/* Output */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <CheckCircle className="text-green-400" size={24} />
                Agent Output
              </h3>
              <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                <pre className="text-slate-200 whitespace-pre-wrap text-sm leading-relaxed">
                  {result.output}
                </pre>
              </div>
            </div>

            {/* Invoice */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <FileText className="text-purple-400" size={24} />
                Invoice
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                  <p className="text-sm text-purple-300 mb-1">Prompt Tokens</p>
                  <p className="text-2xl font-bold text-white">{result.invoice.prompt_tokens?.toLocaleString() || 0}</p>
                </div>
                <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                  <p className="text-sm text-purple-300 mb-1">Completion Tokens</p>
                  <p className="text-2xl font-bold text-white">{result.invoice.completion_tokens?.toLocaleString() || 0}</p>
                </div>
                <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                  <p className="text-sm text-purple-300 mb-1">Total Tokens</p>
                  <p className="text-2xl font-bold text-white">{result.invoice.total_tokens?.toLocaleString() || 0}</p>
                </div>
                <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                  <p className="text-sm text-purple-300 mb-1">Cost (USD)</p>
                  <p className="text-2xl font-bold text-green-400">
                    ${(result.invoice.cost_usd || 0).toFixed(6)}
                  </p>
                </div>
              </div>
            </div>

            {/* Transaction Details */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-purple-500/20">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Link2 className="text-blue-400" size={24} />
                Kite Chain Transactions
              </h3>
              <div className="space-y-4">
                <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                  <p className="text-sm text-purple-300 mb-1">Payment Transaction</p>
                  <a
                    href={getExplorerUrl(result.tx_hash)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 font-mono text-sm break-all flex items-center gap-2"
                  >
                    {result.tx_hash}
                    <Link2 size={14} />
                  </a>
                </div>
                <div className="bg-slate-900/80 rounded-lg p-4 border border-purple-500/20">
                  <p className="text-sm text-purple-300 mb-1">Attestation Hash</p>
                  <div className="flex items-center gap-2">
                    <Hash size={16} className="text-green-400" />
                    <span className="text-green-300 font-mono text-sm break-all">
                      {result.attestation_hash}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-red-500/30">
            <h3 className="text-xl font-bold text-red-400 mb-2">Error</h3>
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-slate-400 text-sm">
          <p>Powered by PayMind · Kite AI Global Hackathon 2026</p>
        </div>
      </div>
    </div>
  );
}

export default App;
