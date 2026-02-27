import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'STOCKSTATS | Quantitative Trading Desk',
  description: 'Institutional-grade statistical arbitrage engine UI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0E1117] text-white font-sans antialiased">
        {/* Navigation Sidebar */}
        <div className="flex h-screen overflow-hidden">
          <aside className="w-64 border-r border-[#1F2937] bg-[#111827] flex flex-col">
            <div className="p-6">
              <h1 className="text-2xl font-bold tracking-tighter bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
                STOCKSTATS
              </h1>
              <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest font-semibold flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Engine Live
              </p>
            </div>

            <nav className="flex-1 px-4 space-y-2 mt-4">
              <a href="#" className="flex items-center gap-3 px-3 py-2 bg-[#1F2937] text-white rounded-lg transition-colors">
                <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span className="font-medium text-sm">Command Center</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-3 py-2 text-gray-400 hover:bg-[#1F2937] hover:text-white rounded-lg transition-colors">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <span className="font-medium text-sm">Cointegration Matrices</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-3 py-2 text-gray-400 hover:bg-[#1F2937] hover:text-white rounded-lg transition-colors">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span className="font-medium text-sm">Risk Parameters</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-3 py-2 text-gray-400 hover:bg-[#1F2937] hover:text-white rounded-lg transition-colors">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium text-sm">Execution Ledger</span>
              </a>
            </nav>

            <div className="p-4 border-t border-[#1F2937]">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-xs font-bold shadow-lg">
                  QT
                </div>
                <div>
                  <p className="text-sm font-medium">Head Trader</p>
                  <p className="text-xs text-gray-400">ADMIN</p>
                </div>
              </div>
            </div>
          </aside>

          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
