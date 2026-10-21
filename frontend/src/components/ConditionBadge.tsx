import type { Condition } from '../api/types'

export function ConditionBadge({ condition }: { condition: Condition }) {
  const secondHand = condition === 'second-hand'

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${
        secondHand ? 'bg-fern/25 text-moss' : 'bg-sand text-stone'
      }`}
    >
      {secondHand ? 'Second-hand' : 'New'}
    </span>
  )
}
