import { useState } from 'react'

import type { AnalysisResponse } from '../api/types'
import { formatKg } from '../lib/format'
import { POINTS_PER_KG } from '../lib/rewards'
import { EditItemsPanel } from './EditItemsPanel'
import { ItemCard } from './ItemCard'
import { OffersSection } from './OffersSection'
import { ResultsSummary } from './ResultsSummary'

type Props = {
  result: AnalysisResponse
  /** Called with the recalculated result after the user edits the items. */
  onUpdate: (result: AnalysisResponse) => void
  onScanAgain: () => void
}

export function ResultsView({ result, onUpdate, onScanAgain }: Props) {
  const [editing, setEditing] = useState(false)
  // True once the user has checked and recalculated the items.
  const [reviewed, setReviewed] = useState(false)
  const count = result.items.length
  const itemsLabel = `${count} ${count === 1 ? 'item' : 'items'}`

  return (
    <section aria-labelledby="results-title" className="space-y-6 pt-4">
      {result.provider === 'mock' && (
        <p className="rounded-2xl border border-ochre/40 bg-ochre/10 px-4 py-3 text-sm text-bark">
          <span className="font-semibold">Demo mode:</span> sample results. Add a Gemini or OpenAI key to scan real
          photos.
        </p>
      )}

      <div>
        <h1 id="results-title" className="font-display text-3xl font-semibold sm:text-4xl">
          {reviewed ? `Your ${itemsLabel}` : `We found ${itemsLabel}`}
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
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-display text-2xl font-semibold">{editing ? 'Edit your items' : 'Your items'}</h2>
          {!editing && (
            <button
              type="button"
              onClick={() => setEditing(true)}
              className="min-h-10 rounded-full border border-moss px-4 text-sm font-semibold text-moss hover:bg-moss/10"
            >
              Edit items
            </button>
          )}
        </div>

        <div className="mt-3">
          {editing ? (
            <EditItemsPanel
              items={result.items}
              onCancel={() => setEditing(false)}
              onSaved={(updated) => {
                setEditing(false)
                setReviewed(true)
                // Recalculating doesn't re-read the photo, so it was still read by the same provider.
                onUpdate({ ...updated, provider: result.provider })
              }}
            />
          ) : (
            <ul className="space-y-3">
              {result.items.map((item, index) => (
                // Items have no id and the same category can appear twice.
                <ItemCard key={`${index}-${item.category}`} item={item} showConfidence={!reviewed} />
              ))}
            </ul>
          )}
        </div>
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
