import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Activity, Terminal, RefreshCw, X } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export default function App() {
  const [metrics, setMetrics] = useState(null);
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [runDetails, setRunDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/runs`);
      const data = await res.json();
      setMetrics(data.metrics);
      setRuns(data.runs);
    } catch (err) {
      console.error("Failed to fetch dashboard metrics", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRunDetails = async (runId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/runs/${runId}`);
      const data = await res.json();
      setRunDetails(data);
    } catch (err) {
      console.error("Failed to fetch run details", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const openInspectorModal = (run) => {
    setSelectedRun(run);
    fetchRunDetails(run.id);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-5">
        <div className="flex items-center space-x-3">
          <Shield className="w-9 h-9 text-indigo-500" />
          <div>
            <h1 className="text-2xl font-bold tracking-tight">RedShield AI Engine</h1>
            <p className="text-xs text-slate-400">CI/CD Automated LLM Red-Teaming & Security Guardrail</p>
          </div>
        </div>
        <button 
          onClick={fetchDashboardData} 
          className="flex items-center space-x-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg text-sm text-slate-300 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </header>

      {/* Summary Metrics Row */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Security Runs</p>
              <p className="text-2xl font-extrabold mt-1 text-slate-100">{metrics.total_runs}</p>
            </div>
            <Activity className="w-8 h-8 text-indigo-400 opacity-80" />
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Pass Rate</p>
              <p className="text-2xl font-extrabold mt-1 text-emerald-400">{metrics.pass_rate_percentage}%</p>
            </div>
            <ShieldCheck className="w-8 h-8 text-emerald-400 opacity-80" />
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Failed Builds</p>
              <p className="text-2xl font-extrabold mt-1 text-rose-400">{metrics.failed_runs}</p>
            </div>
            <ShieldAlert className="w-8 h-8 text-rose-400 opacity-80" />
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg Risk Score</p>
              <p className="text-2xl font-extrabold mt-1 text-amber-400">{metrics.average_risk_score}%</p>
            </div>
            <Terminal className="w-8 h-8 text-amber-400 opacity-80" />
          </div>
        </div>
      )}

      {/* Historical Runs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4 text-slate-200">Historical Red-Teaming Executions</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Run ID</th>
                <th className="px-4 py-3">Repository</th>
                <th className="px-4 py-3">Commit SHA</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Risk Score</th>
                <th className="px-4 py-3">Executed At</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/50 transition">
                  <td className="px-4 py-3 font-mono text-slate-400">#{r.id}</td>
                  <td className="px-4 py-3 font-medium text-slate-200">{r.repository_name}</td>
                  <td className="px-4 py-3 font-mono text-indigo-400">{r.commit_sha.substring(0, 7)}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      r.status === 'PASSED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                      r.status === 'FAILED' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                      'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-semibold">{r.risk_score}%</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{r.created_at}</td>
                  <td className="px-4 py-3 text-right">
                    <button 
                      onClick={() => openInspectorModal(r)}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-md text-xs font-medium transition"
                    >
                      Inspect Logs
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Attack Log Inspector Modal */}
      {selectedRun && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex justify-center items-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
            <div className="p-5 border-b border-slate-800 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-slate-100">Attack Log Inspector — Run #{selectedRun.id}</h3>
                <p className="text-xs text-slate-400 font-mono">Commit: {selectedRun.commit_sha}</p>
              </div>
              <button 
                onClick={() => { setSelectedRun(null); setRunDetails(null); }}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4">
              {!runDetails ? (
                <div className="text-center py-8 text-slate-400">Loading evaluation logs...</div>
              ) : runDetails.results.length === 0 ? (
                <div className="text-center py-8 text-slate-400">No attack results logged for this run.</div>
              ) : (
                runDetails.results.map((res) => (
                  <div key={res.id} className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">{res.category}</span>
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        res.is_vulnerable ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      }`}>
                        {res.is_vulnerable ? 'VULNERABILITY DETECTED' : 'SAFE / DEFENDED'}
                      </span>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 font-medium">Attack Prompt Sent:</p>
                      <p className="text-xs font-mono bg-slate-900 p-2 rounded text-slate-300 mt-1">{res.attack_prompt}</p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 font-medium">Model Raw Response:</p>
                      <p className="text-xs font-mono bg-slate-900 p-2 rounded text-slate-300 mt-1">{res.model_response}</p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 font-medium">Judge Reasoning:</p>
                      <p className="text-xs text-slate-400 italic mt-0.5">{res.judge_reasoning}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}