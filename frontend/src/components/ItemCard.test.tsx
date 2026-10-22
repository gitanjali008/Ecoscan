import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it, vi } from 'vitest'

import type { ScoredItem } from '../api/types'
import { makeItem } from '../test/fixtures'
import { ItemCard } from './ItemCard'

function renderCard(item: ScoredItem, props: Partial<Parameters<typeof ItemCard>[0]> = {}) {
  const onConditionChange = vi.fn()
  render(<ItemCard item={item} onConditionChange={onConditionChange} {...props} />)
  return { onConditionChange }
}

it('uses the scan label as the title and still shows the category and material', () => {
  renderCard(makeItem({ category: 'dress', material: 'polyester', label: 'red floral midi dress' }))

  expect(screen.getByRole('heading')).toHaveTextContent('Red floral midi dress')
  expect(screen.getByText('Dress · Polyester')).toBeInTheDocument()
})

it('falls back to the category when there is no label', () => {
  renderCard(makeItem({ category: 'jeans', material: 'cotton', label: null }))

  expect(screen.getByRole('heading')).toHaveTextContent('Jeans')
  expect(screen.getByText('Cotton')).toBeInTheDocument()
})

it('shows the eco tip', () => {
  renderCard(makeItem({ tip: 'Bought second-hand, this would save 4 kg CO2 (+40 pts).' }))

  expect(screen.getByText('Bought second-hand, this would save 4 kg CO2 (+40 pts).')).toBeInTheDocument()
})

it('asks how the item was got, with the condition from the scan pre-selected', () => {
  renderCard(makeItem({ condition: 'new' }))

  expect(screen.getByRole('group', { name: 'How did you get it?' })).toBeInTheDocument()
  expect(screen.getByRole('radio', { name: 'New' })).toBeChecked()
  expect(screen.getByRole('radio', { name: 'Second-hand' })).not.toBeChecked()
})

it('choosing a chip reports the new condition', async () => {
  const user = userEvent.setup()
  const { onConditionChange } = renderCard(makeItem({ condition: 'new' }))

  await user.click(screen.getByRole('radio', { name: 'Second-hand' }))

  expect(onConditionChange).toHaveBeenCalledWith('second-hand')
})

it('shows that it is updating and locks the chips while disabled', () => {
  renderCard(makeItem(), { updating: true, disabled: true })

  expect(screen.getByRole('status')).toHaveTextContent('Updating…')
  expect(screen.getByRole('radio', { name: 'Second-hand' })).toBeDisabled()
})
