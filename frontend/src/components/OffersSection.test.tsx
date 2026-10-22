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

it('with zero points, encourages the user and shows only the nearest reward', () => {
  render(
    <OffersSection
      offers={{
        points: 0,
        eligible: [],
        locked: [
          makeLockedOffer({ id: 'swap', title: 'Free clothing swap entry', points_required: 30, points_needed: 30 }),
          makeLockedOffer({ id: 'tree', title: 'Plant a tree', points_required: 150, points_needed: 150 }),
        ],
      }}
    />,
  )

  expect(
    screen.getByText('No points yet — mark items you got second-hand, or choose lower-impact materials next time.'),
  ).toBeInTheDocument()
  expect(screen.getByText('Your nearest reward')).toBeInTheDocument()
  expect(screen.getByText('Free clothing swap entry')).toBeInTheDocument()
  expect(screen.getByRole('progressbar', { name: 'Progress towards Free clothing swap entry' })).toBeInTheDocument()
  expect(screen.queryByText('Plant a tree')).not.toBeInTheDocument()
  expect(screen.queryByText('Ready to redeem')).not.toBeInTheDocument()
})

it('with no eligible offers, says how far the first one is', () => {
  render(<OffersSection offers={{ points: 12, eligible: [], locked: [makeLockedOffer({ points_needed: 18 })] }} />)

  expect(screen.getByText('Earn 18 more points to unlock your first offer.')).toBeInTheDocument()
  expect(screen.queryByRole('button', { name: 'Redeem' })).not.toBeInTheDocument()
})
