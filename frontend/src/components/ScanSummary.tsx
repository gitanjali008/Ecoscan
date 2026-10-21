import type { AnalysisResponse } from '../api/types'

type Props = {
  result: AnalysisResponse
  onScanAgain: () => void
}

/** A short summary of a scan. The full per-item results screen replaces this in the next step. */
export function ScanSummary({ result, onScanAgain }: Props) {
  const count = result.items.length

  return (
    <section aria-live="polite" className="rounded-3xl border border-sand bg-white/60 p-6">
      <h2 className="font-display text-2xl font-semibold">
        We found {count} {count === 1 ? 'item' : 'items'}
      </h2>
      <dl className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-2xl bg-clay/10 p-4">
          <dt className="text-sm text-stone">Carbon footprint</dt>
          <dd className="font-display text-2xl font-semibold text-clay">{result.total_carbon_kg} kg</dd>
        </div>
        <div className="rounded-2xl bg-ochre/15 p-4">
          <dt className="text-sm text-stone">Points earned</dt>
          <dd className="font-display text-2xl font-semibold text-ochre">{result.total_points}</dd>
        </div>
      </dl>
      <button
        type="button"
        onClick={onScanAgain}
        className="mt-5 min-h-12 w-full rounded-full border border-moss font-semibold text-moss hover:bg-moss/10"
      >
        Scan another photo
      </button>
    </section>
  )
}
