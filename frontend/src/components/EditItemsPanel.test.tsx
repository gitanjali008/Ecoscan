import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'

import * as client from '../api/client'
import { makeItem } from '../test/fixtures'
import { EditItemsPanel } from './EditItemsPanel'

const offers = { points: 80, eligible: [], locked: [] }
const score = { items: [makeItem()], total_carbon_kg: 2, total_saved_kg: 8, total_points: 80 }

beforeEach(() => {
  vi.spyOn(client, 'getCarbonFactors').mockResolvedValue({
    base_kg: { jeans: 10 },
    default_kg: 7,
    material_factor: { cotton: 1 },
    condition_factor: { new: 1, 'second-hand': 0.2 },
  })
})

it('sends the edited items to scoreItems, then fetches offers for the new points', async () => {
  const user = userEvent.setup()
  const scoreItems = vi.spyOn(client, 'scoreItems').mockResolvedValue(score)
  const getOffers = vi.spyOn(client, 'getOffers').mockResolvedValue(offers)
  const onSaved = vi.fn()
  render(
    <EditItemsPanel
      items={[makeItem({ category: 'jeans', material: 'unknown' }), makeItem({ category: 'hat' })]}
      onSaved={onSaved}
      onCancel={() => {}}
    />,
  )

  // Item 1: mark as second-hand. Item 2: remove it.
  const [firstCondition] = screen.getAllByLabelText('Condition')
  await user.selectOptions(firstCondition, 'second-hand')
  await user.click(screen.getAllByRole('button', { name: 'Remove' })[1])
  await user.click(screen.getByRole('button', { name: 'Recalculate' }))

  expect(scoreItems).toHaveBeenCalledWith([
    { category: 'jeans', material: '', condition: 'second-hand', confidence: 0.9, label: null },
  ])
  expect(getOffers).toHaveBeenCalledWith(80)
  expect(onSaved).toHaveBeenCalledWith({ ...score, offers })
})

it('keeps the scan label unless the item type is changed', async () => {
  const user = userEvent.setup()
  const scoreItems = vi.spyOn(client, 'scoreItems').mockResolvedValue(score)
  vi.spyOn(client, 'getOffers').mockResolvedValue(offers)
  render(
    <EditItemsPanel
      items={[makeItem({ category: 'dress', label: 'red midi dress' }), makeItem({ category: 'jeans', label: 'blue jeans' })]}
      onSaved={() => {}}
      onCancel={() => {}}
    />,
  )

  const [, secondType] = screen.getAllByLabelText('Type')
  await user.clear(secondType)
  await user.type(secondType, 'shorts')
  await user.click(screen.getByRole('button', { name: 'Recalculate' }))

  const [[sent]] = scoreItems.mock.calls
  expect(sent.map((item) => item.label)).toEqual(['red midi dress', null])
})

it('asks for a type instead of calling the API when a category is empty', async () => {
  const user = userEvent.setup()
  const scoreItems = vi.spyOn(client, 'scoreItems')
  render(<EditItemsPanel items={[makeItem()]} onSaved={() => {}} onCancel={() => {}} />)

  await user.clear(screen.getByLabelText('Type'))
  await user.click(screen.getByRole('button', { name: 'Recalculate' }))

  expect(screen.getByRole('alert')).toHaveTextContent('Every item needs a type')
  expect(scoreItems).not.toHaveBeenCalled()
})

it('shows a retryable error when recalculating fails', async () => {
  const user = userEvent.setup()
  vi.spyOn(client, 'scoreItems').mockRejectedValue(new client.ApiError('network_error', 'offline', 0))
  render(<EditItemsPanel items={[makeItem()]} onSaved={() => {}} onCancel={() => {}} />)

  await user.click(screen.getByRole('button', { name: 'Recalculate' }))

  expect(await screen.findByText("Can't reach EcoScan")).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
})
