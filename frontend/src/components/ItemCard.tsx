import type { ScoredItem } from '../api/types'
import { capitalize, formatKg } from '../lib/format'
import { CarbonBar } from './CarbonBar'
import { ConditionBadge } from './ConditionBadge'

export function ItemCard({ item }: { item: ScoredItem }) {
  const material = item.material === 'unknown' ? 'Material unknown' : capitalize(item.material)

  return (
    <li className="rounded-3xl border border-sand bg-white/60 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-display text-xl font-semibold">{capitalize(item.category)}</h3>
          <p className="text-stone">{material}</p>
        </div>
        <ConditionBadge condition={item.condition} />
      </div>

      <div className="mt-4">
        <CarbonBar baselineKg={item.baseline_kg} actualKg={item.actual_kg} />
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-sand pt-3 text-sm">
        <span className="text-stone">{Math.round(item.confidence * 100)}% sure</span>
        <span>
          <span className={item.saved_kg > 0 ? 'font-semibold text-moss' : 'text-stone'}>
            {formatKg(item.saved_kg)} saved
          </span>
          <span className="text-stone"> · </span>
          <span className="font-semibold text-ochre">+{item.points} pts</span>
        </span>
      </div>
    </li>
  )
}
