import { useId } from 'react'

import type { Condition } from '../api/types'

export type DraftItem = {
  /** Local key so React keeps the right row when one is removed. */
  key: number
  category: string
  material: string
  condition: Condition
  confidence: number
}

type Props = {
  item: DraftItem
  index: number
  categoryListId: string
  materialListId: string
  disabled: boolean
  onChange: (patch: Partial<DraftItem>) => void
  onRemove: () => void
}

const inputClass =
  'mt-1 block min-h-12 w-full rounded-xl border border-sand bg-white px-3 text-base text-bark focus:border-moss focus:outline-2 focus:outline-moss/30 disabled:opacity-60'

export function ItemEditor({ item, index, categoryListId, materialListId, disabled, onChange, onRemove }: Props) {
  const id = useId()

  return (
    <li className="space-y-3 rounded-3xl border border-sand bg-white/70 p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-stone">Item {index + 1}</span>
        <button
          type="button"
          onClick={onRemove}
          disabled={disabled}
          className="text-sm font-semibold text-clay hover:underline disabled:opacity-50"
        >
          Remove
        </button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <label htmlFor={`${id}-category`} className="block text-sm font-semibold">
          Type
          <input
            id={`${id}-category`}
            list={categoryListId}
            value={item.category}
            onChange={(e) => onChange({ category: e.target.value })}
            placeholder="e.g. t-shirt"
            required
            disabled={disabled}
            className={inputClass}
          />
        </label>
        <label htmlFor={`${id}-material`} className="block text-sm font-semibold">
          Material
          <input
            id={`${id}-material`}
            list={materialListId}
            value={item.material}
            onChange={(e) => onChange({ material: e.target.value })}
            placeholder="e.g. organic cotton"
            disabled={disabled}
            className={inputClass}
          />
        </label>
      </div>

      <label htmlFor={`${id}-condition`} className="block text-sm font-semibold">
        Condition
        <select
          id={`${id}-condition`}
          value={item.condition}
          onChange={(e) => onChange({ condition: e.target.value as Condition })}
          disabled={disabled}
          className={inputClass}
        >
          <option value="new">New</option>
          <option value="second-hand">Second-hand</option>
        </select>
      </label>
    </li>
  )
}
