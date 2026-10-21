import type { AnalysisResponse } from '../api/types'
import { formatKg } from '../lib/format'
import { POINTS_PER_KG } from '../lib/rewards'
import { ItemCard } from './ItemCard'
import { OffersSection } from './OffersSection'
import { ResultsSummary } from './ResultsSummary'

type Props = {
  result: AnalysisResponse
  onScanAgain: () => void
}

export function ResultsView({ result, onScanAgain }: Props) {
  const count = result.items.length

  return (
    <section aria-labelledby="results-title" className="space-y-6 pt-4">
      <div>
        <h1 id="results-title" className="font-display text-3xl font-semibold sm:text-4xl">
          We found {count} {count === 1 ? 'item' : 'items'}
        </h1>
        <p className="mt-2 text-lg text-stone">
          {result.total_saved_kg > 0
            ? `You saved ${formatKg(result.total_saved_kg)} of CO2 compared with buying everything new.`
            : 'Choosing second-hand or lower-impact materials next time would save carbon and earn points.'}
        </p>
      </div>

      <ResultsSummary result={result} />

      <p className="rounded-2xl border border-sand p-4 text-sm text-stone">
        <span className="font-semibold text-bark">How points work:</span> every 1 kg of CO2 saved earns{' '}
        {POINTS_PER_KG} points. You save carbon by choosing second-hand items or lower-impact materials like
        organic cotton, linen or hemp.
      </p>

      <div>
        <h2 className="font-display text-2xl font-semibold">Your items</h2>
        <ul className="mt-3 space-y-3">
          {result.items.map((item, index) => (
            // Items have no id and the same category can appear twice.
            <ItemCard key={`${index}-${item.category}`} item={item} />
          ))}
        </ul>
      </div>

      <OffersSection offers={result.offers} />

      <button
        type="button"
        onClick={onScanAgain}
        className="min-h-14 w-full rounded-full bg-moss text-lg font-semibold text-linen hover:bg-moss-dark"
      >
        Scan another photo
      </button>
    </section>
  )
}
