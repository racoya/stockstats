export default function DashboardPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header section */}
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-light tracking-tight text-white mb-2">Command Center</h2>
          <p className="text-gray-400">Quantitative models and execution routing active.</p>
        </div>

        <div className="text-right">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">Global Portfolio VaR (95%)</p>
          <p className="text-2xl font-mono text-red-400">$-42,500.00</p>
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        {/* Metric 1: HMM Regime */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">Market Regime (HMM)</h3>
          <p className="text-3xl font-light text-white mb-1"><span className="text-blue-400 font-medium">State 0</span></p>
          <p className="text-sm text-gray-400">Low Volatility (Ranging)</p>
          <div className="mt-4 pt-4 border-t border-[#1F2937] flex justify-between items-center text-xs">
            <span className="text-emerald-400 flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" /></svg>
              Mean Reversion AUTHD
            </span>
          </div>
        </div>

        {/* Metric 2: GARCH Volatility */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">BTC GARCH(1,1)</h3>
          <p className="text-3xl font-mono text-white mb-1">2.41<span className="text-xl text-gray-500">%</span></p>
          <p className="text-sm text-gray-400">Conditional StdDev</p>
          <div className="mt-4 pt-4 border-t border-[#1F2937] flex justify-between items-center text-xs">
            <span className="text-gray-400">Bands Expaned</span>
            <span className="text-gray-500 font-mono">ω=0.01 α=0.15 β=0.84</span>
          </div>
        </div>

        {/* Metric 3: Toxicity (OBI) */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">L2 Toxicity (OBI)</h3>
          <p className="text-3xl font-mono text-emerald-400 mb-1">-0.12</p>
          <p className="text-sm text-gray-400">Order Book Imbalance</p>
          <div className="mt-4 pt-4 border-t border-[#1F2937] flex justify-between items-center text-xs">
            <span className="text-emerald-400 flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
              Optimal Execution
            </span>
          </div>
        </div>

        {/* Metric 4: Hampel Filter */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-orange-500/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">Hampel Filter (MAD)</h3>
          <p className="text-3xl font-mono text-white mb-1">14</p>
          <p className="text-sm text-gray-400">Rogue Ticks Scrubbed (24h)</p>
          <div className="mt-4 pt-4 border-t border-[#1F2937] flex justify-between items-center text-xs">
            <span className="text-gray-400">Current MAD Multiplier</span>
            <span className="text-gray-500 font-mono">3.0σ</span>
          </div>
        </div>
      </div>

      {/* Active Cointegration Spreads Table */}
      <div className="bg-[#111827] border border-[#1F2937] rounded-xl shadow-xl overflow-hidden mt-8">
        <div className="px-6 py-5 border-b border-[#1F2937] flex justify-between items-center bg-[#18212F]">
          <h3 className="text-lg font-medium text-white flex items-center gap-3">
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Active Cointegration Matrices
          </h3>
          <span className="px-3 py-1 bg-[#1F2937] text-gray-300 text-xs rounded-full font-mono font-bold tracking-wider">
            LIVE FEEDS
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#1F2937] bg-[#111827]">
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-widest">Asset Pair</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-widest text-right">Hedge Ratio (β)</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-widest text-right">ADF Stationarity (p-value)</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-widest text-right">Spread Z-Score</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-widest text-right">Signal</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F2937]">

              <tr className="hover:bg-[#18212F]/50 transition-colors group">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-white font-medium">BTC/USDT</span>
                    <span className="text-gray-500 font-light">vs</span>
                    <span className="font-mono text-white font-medium">ETH/USDT</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-mono text-gray-300">
                  14.521
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs border border-emerald-500/20">
                    0.0211 {"<"} 0.05
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-mono text-white">
                  +2.14σ
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-bold tracking-wider border border-red-500/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                    SHORT SPREAD
                  </span>
                </td>
              </tr>

              <tr className="hover:bg-[#18212F]/50 transition-colors group">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-white font-medium">SOL/USDT</span>
                    <span className="text-gray-500 font-light">vs</span>
                    <span className="font-mono text-white font-medium">AVAX/USDT</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-mono text-gray-300">
                  3.119
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs border border-emerald-500/20">
                    0.0482 {"<"} 0.05
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-mono text-gray-400">
                  -0.41σ
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#1F2937] text-gray-400 text-xs font-bold tracking-wider border border-[#374151]">
                    HOLD
                  </span>
                </td>
              </tr>

              <tr className="hover:bg-[#18212F]/50 transition-colors group">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-white font-medium">AAPL</span>
                    <span className="text-gray-500 font-light">vs</span>
                    <span className="font-mono text-white font-medium">MSFT</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-mono text-gray-500">
                  --
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="px-2 py-1 rounded-md bg-red-500/10 text-red-400 font-mono text-xs border border-red-500/20">
                    0.4102 {">"} 0.05
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-mono text-gray-600">
                  Random Walk
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 text-gray-600 text-xs font-bold tracking-wider">
                    VETO (NON-STATIONARY)
                  </span>
                </td>
              </tr>

            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
