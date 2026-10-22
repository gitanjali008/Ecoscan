import { useCallback, useState } from 'react'

import type { Offer, OffersResponse } from '../api/types'
import { EligibleOfferCard } from './EligibleOfferCard'
import { LockedOfferCard } from './LockedOfferCard'
import { Toast } from './Toast'

export function OffersSection({ offers }: { offers: OffersResponse }) {
  const [redeemed, setRedeemed] = useState<Set<string>>(new Set())
  const [toast, setToast] = useState<string | null>(null)
  const closeToast = useCallback(() => setToast(null), [])

  // Demo only: there are no user accounts, so nothing is sent to the backend.
  function redeem(offer: Offer) {
    setRedeemed((previous) => new Set(previous).add(offer.id))
    setToast(`Redeemed "${offer.title}" from ${offer.partner}. This is a demo, so no voucher is sent.`)
  }

  const { eligible, locked, points } = offers

  // Nothing earned yet: encourage, and show only the nearest goal (locked offers come cheapest first).
  if (points === 0 && eligible.length === 0) {
    const nearest = locked[0]
    return (
      <section aria-labelledby="offers-title" className="space-y-4">
        <h2 id="offers-title" className="font-display text-2xl font-semibold">
          Your rewards
        </h2>
        <p className="rounded-2xl bg-sand/50 p-4 text-stone">
          No points yet — mark items you got second-hand, or choose lower-impact materials next time.
        </p>
        {nearest && (
          <div>
            <h3 className="font-semibold">Your nearest reward</h3>
            <ul className="mt-3">
              <LockedOfferCard offer={nearest} points={0} />
            </ul>
          </div>
        )}
      </section>
    )
  }

  return (
    <section aria-labelledby="offers-title" className="space-y-6">
      <h2 id="offers-title" className="font-display text-2xl font-semibold">
        Your rewards
      </h2>

      <div>
        <h3 className="font-semibold">Ready to redeem</h3>
        {eligible.length > 0 ? (
          <ul className="mt-3 grid gap-3 sm:grid-cols-2">
            {eligible.map((offer) => (
              <EligibleOfferCard key={offer.id} offer={offer} redeemed={redeemed.has(offer.id)} onRedeem={redeem} />
            ))}
          </ul>
        ) : (
          <p className="mt-2 rounded-2xl bg-sand/50 p-4 text-stone">
            {locked.length > 0
              ? `Earn ${locked[0].points_needed} more points to unlock your first offer.`
              : 'There are no offers right now.'}
          </p>
        )}
      </div>

      {locked.length > 0 ? (
        <div>
          <h3 className="font-semibold">Almost there</h3>
          <ul className="mt-3 space-y-3">
            {locked.map((offer) => (
              <LockedOfferCard key={offer.id} offer={offer} points={points} />
            ))}
          </ul>
        </div>
      ) : (
        eligible.length > 0 && <p className="text-moss">You've unlocked every offer. Nice work!</p>
      )}

      {toast && <Toast message={toast} onClose={closeToast} />}
    </section>
  )
}
