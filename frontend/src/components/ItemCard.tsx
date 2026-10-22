import { useId } from 'react'

import type { Condition, ScoredItem } from '../api/types'
import { capitalize, formatKg } from '../lib/format'
import { CarbonBar } from './CarbonBar'

const CONDITIONS: { value: Condition; label: string }[] = [
  { value: 'new', label: 'New' },
  { value: 'second-hand', label: 'Second-hand' },
]

type Props = {
  item: ScoredItem
  /** False once the user has checked the items: the AI's confidence no longer matters. */
  showConfidence?: boolean
  /** Called when the user says how they got the item. A photo can't show it, so the AI usually guesses "new". */
  onConditionChange: (condition: Condition) => void
  /** True while this item is being scored again. */
  updating?: boolean
  /** True while any item is being scored again, so only one change runs at a time. */
  disabled?: boolean
}

export function ItemCard({ item, showConfidence = true, onConditionChange, updating = false, disabled = false }: Props) {
  const name = useId()
  const material = item.material === 'unknown' ? 'Material unknown' : capitalize(item.material)
  // The scan's description reads better than the bare category; the category still shows below it.
  const title = capitalize(item.label ?? item.category)
  const details = item.label ? `${capitalize(item.category)} · ${material}` : material

  return (
    <li className="rounded-3xl border border-sand bg-white/60 p-5">
      <div className="min-w-0">
        <h3 className="font-display text-xl font-semibold">{title}</h3>
        <p className="text-stone">{details}</p>
      </div>

      <fieldset disabled={disabled} className="mt-4">
        <legend className="text-sm font-semibold">How did you get it?</legend>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          {CONDITIONS.map(({ value, label }) => (
            <label
              key={value}
              className="min-h-10 cursor-pointer rounded-full border border-sand px-4 py-2 text-sm font-semibold text-stone hover:border-moss has-checked:border-moss has-checked:bg-moss has-checked:text-linen has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-moss has-disabled:cursor-not-allowed has-disabled:opacity-60"
            >
              <input
                type="radio"
                name={name}
                value={value}
                checked={item.condition === value}
                onChange={() => onConditionChange(value)}
                className="sr-only"
              />
              {label}
            </label>
          ))}
          {updating && (
            <span role="status" className="text-sm text-stone">
              Updating…
            </span>
          )}
        </div>
      </fieldset>

      <div className="mt-4">
        <CarbonBar baselineKg={item.baseline_kg} actualKg={item.actual_kg} />
      </div>

      {item.tip && <p className="mt-4 rounded-2xl bg-fern/15 px-4 py-3 text-sm text-bark">{item.tip}</p>}

      <div className="mt-4 flex items-center justify-between border-t border-sand pt-3 text-sm">
        <span className="text-stone">
          {showConfidence ? `${Math.round(item.confidence * 100)}% sure` : 'Checked by you'}
        </span>
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
