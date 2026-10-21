import { useEffect, useId, useState } from 'react'

import { getCarbonFactors, getOffers, scoreItems } from '../api/client'
import type { AnalysisResponse, ScoredItem } from '../api/types'
import { ErrorNotice } from './ErrorNotice'
import { ItemEditor, type DraftItem } from './ItemEditor'

type Props = {
  items: ScoredItem[]
  onSaved: (result: AnalysisResponse) => void
  onCancel: () => void
}

let nextKey = 0

function toDrafts(items: ScoredItem[]): DraftItem[] {
  return items.map((item) => ({
    key: nextKey++,
    category: item.category,
    // An empty field reads better than "unknown"; the backend turns it back into "unknown".
    material: item.material === 'unknown' ? '' : item.material,
    condition: item.condition,
    confidence: item.confidence,
  }))
}

export function EditItemsPanel({ items, onSaved, onCancel }: Props) {
  const [drafts, setDrafts] = useState(() => toDrafts(items))
  const [suggestions, setSuggestions] = useState({ categories: [] as string[], materials: [] as string[] })
  const [problem, setProblem] = useState<string | null>(null)
  const [error, setError] = useState<unknown>(null)
  const [saving, setSaving] = useState(false)
  const categoryListId = useId()
  const materialListId = useId()

  // Suggestions are a nice-to-have: free text still works if they fail to load.
  useEffect(() => {
    let active = true
    getCarbonFactors()
      .then((factors) => {
        if (active) {
          setSuggestions({ categories: Object.keys(factors.base_kg), materials: Object.keys(factors.material_factor) })
        }
      })
      .catch(() => {})
    return () => {
      active = false
    }
  }, [])

  function update(key: number, patch: Partial<DraftItem>) {
    setDrafts((current) => current.map((d) => (d.key === key ? { ...d, ...patch } : d)))
  }

  function remove(key: number) {
    setDrafts((current) => current.filter((d) => d.key !== key))
  }

  async function recalculate() {
    if (drafts.some((d) => !d.category.trim())) {
      setProblem('Every item needs a type, for example "t-shirt".')
      return
    }
    setProblem(null)
    setError(null)
    setSaving(true)
    try {
      const score = await scoreItems(
        drafts.map(({ category, material, condition, confidence }) => ({ category, material, condition, confidence })),
      )
      const offers = await getOffers(score.total_points)
      onSaved({ ...score, offers })
    } catch (e) {
      setError(e)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-stone">
        Fix anything we got wrong, then recalculate. Marking an item as second-hand or choosing its real material can
        change its footprint a lot.
      </p>

      <ul className="space-y-3">
        {drafts.map((draft, index) => (
          <ItemEditor
            key={draft.key}
            item={draft}
            index={index}
            categoryListId={categoryListId}
            materialListId={materialListId}
            disabled={saving}
            onChange={(patch) => update(draft.key, patch)}
            onRemove={() => remove(draft.key)}
          />
        ))}
      </ul>

      <datalist id={categoryListId}>
        {suggestions.categories.map((c) => (
          <option key={c} value={c} />
        ))}
      </datalist>
      <datalist id={materialListId}>
        {suggestions.materials.map((m) => (
          <option key={m} value={m} />
        ))}
      </datalist>

      {drafts.length === 0 && (
        <p className="rounded-2xl bg-sand/50 p-4 text-stone">
          You've removed every item. Cancel to keep the original items, or scan another photo.
        </p>
      )}
      {problem && (
        <p role="alert" className="rounded-2xl bg-clay/10 p-4 text-clay">
          {problem}
        </p>
      )}
      {error !== null && <ErrorNotice error={error} onRetry={recalculate} />}

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={onCancel}
          disabled={saving}
          className="min-h-12 rounded-full border border-sand px-6 font-semibold hover:bg-sand/50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={recalculate}
          disabled={saving || drafts.length === 0}
          className="min-h-12 rounded-full bg-moss px-6 font-semibold text-linen hover:bg-moss-dark disabled:opacity-50"
        >
          {saving ? 'Recalculating…' : 'Recalculate'}
        </button>
      </div>
    </div>
  )
}
