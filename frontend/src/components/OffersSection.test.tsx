import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it } from 'vitest'

import { makeLockedOffer, makeOffer } from '../test/fixtures'
import { OffersSection } from './OffersSection'

it('redeeming an offer shows a confirmation and disables the button', async () => {
  const user = userEvent.setup()
  render(<OffersSection offers={{ points: 40, eligible: [makeOffer()], locked: [] }} />)

  await user.click(screen.getByRole('button', { name: 'Redeem' }))

  expect(screen.getByRole('status')).toHaveTextContent('Redeemed "Free clothing swap entry" from Swap Circle')
  expect(screen.getByRole('button', { name: 'Redeemed ✓' })).toBeDisabled()
})

it('with no eligible offers, says how far the first one is', () => {
  render(<OffersSection offers={{ points: 12, eligible: [], locked: [makeLockedOffer({ points_needed: 18 })] }} />)

  expect(screen.getByText('Earn 18 more points to unlock your first offer.')).toBeInTheDocument()
  expect(screen.queryByRole('button', { name: 'Redeem' })).not.toBeInTheDocument()
})
