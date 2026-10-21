import type { ScoreResponse } from '../api/types'
import { formatKg } from '../lib/format'

type StatProps = {
  label: string
  value: string
  hint: string
  className: string
}

function Stat({ label, value, hint, className }: StatProps) {
  return (
    <div className={`rounded-2xl p-4 ${className}`}>
      <dt className="text-sm font-semibold">{label}</dt>
      <dd className="mt-1 font-display text-3xl font-semibold tabular-nums sm:text-4xl">{value}</dd>
      <dd className="text-sm opacity-80">{hint}</dd>
    </div>
  )
}

export function ResultsSummary({ result }: { result: ScoreResponse }) {
  return (
    <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <Stat
        label="Carbon footprint"
        value={formatKg(result.total_carbon_kg)}
        hint="CO2e for these items"
        className="col-span-2 bg-clay/10 text-clay sm:col-span-1"
      />
      <Stat label="CO2 saved" value={formatKg(result.total_saved_kg)} hint="vs buying new" className="bg-fern/20 text-moss" />
      <Stat label="Points" value={String(result.total_points)} hint="earned" className="bg-ochre/15 text-ochre" />
    </dl>
  )
}
