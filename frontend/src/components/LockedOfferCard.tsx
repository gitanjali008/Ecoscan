import type { LockedOffer } from '../api/types'
import { ProgressBar } from './ProgressBar'

type Props = {
  offer: LockedOffer
  points: number
}

export function LockedOfferCard({ offer, points }: Props) {
  return (
    <li className="rounded-3xl border border-sand bg-white/40 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="font-display text-lg leading-snug font-semibold">{offer.title}</h4>
          <p className="text-sm text-stone">{offer.partner}</p>
        </div>
        <span className="shrink-0 rounded-full bg-sand px-2.5 py-0.5 text-xs font-semibold text-stone">
          {offer.points_required} pts
        </span>
      </div>
      <div className="mt-4">
        <ProgressBar value={points} max={offer.points_required} label={`Progress towards ${offer.title}`} />
        <div className="mt-1.5 flex justify-between text-sm">
          <span className="text-stone tabular-nums">
            {points} / {offer.points_required}
          </span>
          <span className="font-semibold text-ochre">{offer.points_needed} more points to unlock</span>
        </div>
      </div>
    </li>
  )
}
