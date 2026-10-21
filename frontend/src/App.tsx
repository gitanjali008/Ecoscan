import { useState } from 'react'

import type { AnalysisResponse } from './api/types'
import { HowItWorks } from './components/HowItWorks'
import { Logo } from './components/Logo'
import { ResultsView } from './components/ResultsView'
import { ScanPanel } from './components/ScanPanel'

function App() {
  const [result, setResult] = useState<AnalysisResponse | null>(null)

  // Switching screens: start each one at the top, not where the Scan button was.
  function show(next: AnalysisResponse | null) {
    setResult(next)
    window.scrollTo({ top: 0 })
  }

  return (
    <div className="mx-auto flex min-h-dvh max-w-xl flex-col px-5 pb-10 sm:px-8">
      <header className="py-5">
        <Logo />
      </header>

      <main className="flex-1 space-y-10">
        {result ? (
          <ResultsView result={result} onScanAgain={() => show(null)} />
        ) : (
          <>
            <section className="pt-6 sm:pt-12">
              <p className="text-sm font-semibold tracking-widest text-fern uppercase">Clothing carbon scanner</p>
              <h1 className="mt-3 font-display text-4xl leading-tight font-semibold sm:text-5xl">
                What does your outfit <span className="text-clay italic">cost</span> the planet?
              </h1>
              <p className="mt-4 text-lg text-stone">
                Scan your clothes to see each item's carbon footprint, and get rewarded for the greener choices
                you already make.
              </p>
            </section>

            <ScanPanel onResult={show} />

            <HowItWorks />
          </>
        )}
      </main>

      <footer className="pt-10 text-sm text-stone">
        Carbon numbers are illustrative estimates, not audited life-cycle data.
      </footer>
    </div>
  )
}

export default App
