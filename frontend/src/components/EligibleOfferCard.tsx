import type { Offer } from '../api/types'

type Props = {
  offer: Offer
  redeemed: boolean
  onRedeem: (offer: Offer) => void
}

export function EligibleOfferCard({ offer, redeemed, onRedeem }: Props) {
  return (
    <li className="flex flex-col rounded-3xl border border-fern/60 bg-white/70 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="font-display text-lg leading-snug font-semibold">{offer.title}</h4>
          <p className="text-sm text-stone">{offer.partner}</p>
        </div>
        <span className="shrink-0 rounded-full bg-ochre/15 px-2.5 py-0.5 text-xs font-semibold text-ochre">
          {offer.points_required} pts
        </span>
      </div>
      <p className="mt-2 flex-1 text-stone">{offer.description}</p>
      <button
        type="button"
        onClick={() => onRedeem(offer)}
        disabled={redeemed}
        className="mt-4 min-h-12 rounded-full bg-moss font-semibold text-linen hover:bg-moss-dark disabled:bg-fern/30 disabled:text-moss"
      >
        {redeemed ? 'Redeemed ✓' : 'Redeem'}
      </button>
    </li>
  )
}
