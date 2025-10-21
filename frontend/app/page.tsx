'use client'

import { useState, useEffect } from 'react'

export default function Home() {
  const [apiStatus, setApiStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
      .then(res => res.json())
      .then(data => {
        setApiStatus(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('API connection failed:', err)
        setLoading(false)
      })
  }, [])

  return (
    <main className="min-h-screen p-8 bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AIcoin Trading System
          </h1>
          <p className="text-xl text-gray-300">
            AI-powered cryptocurrency trading platform
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {/* API Status Card */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-blue-400">API Status</h2>
            {loading ? (
              <p className="text-gray-400">Loading...</p>
            ) : apiStatus ? (
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400 font-semibold">{apiStatus.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Version:</span>
                  <span className="text-white">{apiStatus.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Trading:</span>
                  <span className={apiStatus.trading_enabled ? 'text-green-400' : 'text-red-400'}>
                    {apiStatus.trading_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-red-400">Failed to connect to API</p>
            )}
          </div>

          {/* System Info Card */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-purple-400">System Info</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Frontend:</span>
                <span className="text-green-400">Running</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Database:</span>
                <span className="text-green-400">PostgreSQL</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cache:</span>
                <span className="text-green-400">Redis</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">AI Model:</span>
                <span className="text-blue-400">DeepSeek</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-12">
          <h2 className="text-2xl font-bold mb-4 text-green-400">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/docs`}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              📚 API Docs
            </button>
            <button
              onClick={async () => {
                try {
                  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/trading/decision`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol: 'BTC-PERP', force: true })
                  })
                  const data = await res.json()
                  alert(`Decision: ${JSON.stringify(data, null, 2)}`)
                } catch (err) {
                  alert('Error: ' + err)
                }
              }}
              className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              🤖 Test AI Decision
            </button>
            <button
              onClick={async () => {
                try {
                  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/account/info`)
                  const data = await res.json()
                  alert(`Account: ${JSON.stringify(data, null, 2)}`)
                } catch (err) {
                  alert('Error: ' + err)
                }
              }}
              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              💰 View Account
            </button>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-4xl mb-4">🧠</div>
            <h3 className="text-xl font-bold mb-2">AI Decision Engine</h3>
            <p className="text-gray-400">
              DeepSeek-powered trading decisions with confidence scoring and risk management
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-2">Real-time Trading</h3>
            <p className="text-gray-400">
              Automated trading execution on Hyperliquid with low-latency order placement
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-4xl mb-4">🛡️</div>
            <h3 className="text-xl font-bold mb-2">Risk Control</h3>
            <p className="text-gray-400">
              Multi-layer risk management with position limits, stop-loss, and drawdown protection
            </p>
          </div>
        </div>

        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>AIcoin Trading System v1.0.0 | Powered by DeepSeek AI & Hyperliquid</p>
        </footer>
      </div>
    </main>
  )
}

