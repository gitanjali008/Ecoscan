import { formatKg } from '../lib/format'

type Props = {
  baselineKg: number
  actualKg: number
}

/** Two bars on the same scale: the item bought new vs this item. */
export function CarbonBar({ baselineKg, actualKg }: Props) {
  // Scale to the larger value: a high-impact material can exceed the baseline.
  const max = Math.max(baselineKg, actualKg, 0.01)
  const rows = [
    { label: 'If bought new', kg: baselineKg, bar: 'bg-stone/30' },
    { label: 'This item', kg: actualKg, bar: 'bg-clay' },
  ]

  return (
    <div
      role="img"
      aria-label={`${formatKg(baselineKg)} CO2 if bought new, ${formatKg(actualKg)} for this item`}
      className="space-y-2"
    >
      {rows.map((row) => (
        <div key={row.label} aria-hidden="true">
          <div className="flex justify-between text-sm">
            <span className="text-stone">{row.label}</span>
            <span className="font-semibold tabular-nums">{formatKg(row.kg)}</span>
          </div>
          <div className="mt-1 h-2.5 overflow-hidden rounded-full bg-sand/70">
            <div className={`h-full rounded-full ${row.bar}`} style={{ width: `${(row.kg / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  )
}
