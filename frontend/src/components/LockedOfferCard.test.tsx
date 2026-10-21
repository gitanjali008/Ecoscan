import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'

import { makeLockedOffer } from '../test/fixtures'
import { LockedOfferCard } from './LockedOfferCard'

it('shows how many more points unlock the offer', () => {
  render(<LockedOfferCard offer={makeLockedOffer({ points_required: 150, points_needed: 18 })} points={132} />)

  expect(screen.getByText('Plant a tree')).toBeInTheDocument()
  expect(screen.getByText('18 more points to unlock')).toBeInTheDocument()
  expect(screen.getByText('132 / 150')).toBeInTheDocument()
})

it('exposes the progress to screen readers', () => {
  render(<LockedOfferCard offer={makeLockedOffer({ points_required: 150, points_needed: 18 })} points={132} />)

  const bar = screen.getByRole('progressbar', { name: 'Progress towards Plant a tree' })
  expect(bar).toHaveAttribute('aria-valuenow', '132')
  expect(bar).toHaveAttribute('aria-valuemax', '150')
})
