import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it, vi } from 'vitest'

import * as client from '../api/client'
import type { AnalysisResponse } from '../api/types'
import { makeItem } from '../test/fixtures'
import { ResultsView } from './ResultsView'

const DEMO = 'Demo mode: sample results. Add a Gemini or OpenAI key to scan real photos.'

function makeResult(provider: string): AnalysisResponse {
  return {
    items: [makeItem({ category: 'jeans' })],
    total_carbon_kg: 10,
    total_saved_kg: 0,
    total_points: 0,
    offers: { points: 0, eligible: [], locked: [] },
    provider,
  }
}

it('shows the demo-mode banner for mock results', () => {
  render(<ResultsView result={makeResult('mock')} onUpdate={() => {}} onScanAgain={() => {}} />)

  expect(screen.getByText(/Demo mode:/).closest('p')).toHaveTextContent(DEMO)
})

it.each(['gemini', 'openai'])('has no banner for real %s results', (provider) => {
  render(<ResultsView result={makeResult(provider)} onUpdate={() => {}} onScanAgain={() => {}} />)

  expect(screen.queryByText(/Demo mode/)).not.toBeInTheDocument()
})

it('changing how an item was got rescores it and updates totals and offers', async () => {
  const user = userEvent.setup()
  const rescored = {
    items: [makeItem({ category: 'jeans', condition: 'second-hand', saved_kg: 8, points: 80 })],
    total_carbon_kg: 2,
    total_saved_kg: 8,
    total_points: 80,
  }
  const offers = { points: 80, eligible: [], locked: [] }
  let finishScoring: (score: typeof rescored) => void = () => {}
  const scoreItems = vi.spyOn(client, 'scoreItems').mockReturnValue(new Promise((resolve) => (finishScoring = resolve)))
  const getOffers = vi.spyOn(client, 'getOffers').mockResolvedValue(offers)
  const onUpdate = vi.fn()
  render(<ResultsView result={makeResult('gemini')} onUpdate={onUpdate} onScanAgain={() => {}} />)

  await user.click(screen.getByRole('radio', { name: 'Second-hand' }))

  // While the API answers: a small loading state, and no other change can start.
  expect(screen.getByRole('status')).toHaveTextContent('Updating…')
  expect(screen.getByRole('radio', { name: 'New' })).toBeDisabled()
  expect(screen.getByRole('button', { name: 'Edit items' })).toBeDisabled()
  expect(scoreItems).toHaveBeenCalledWith([
    { category: 'jeans', material: 'cotton', condition: 'second-hand', confidence: 0.9, label: null },
  ])

  finishScoring(rescored)

  await waitFor(() => expect(onUpdate).toHaveBeenCalledWith({ ...rescored, offers, provider: 'gemini' }))
  expect(getOffers).toHaveBeenCalledWith(80)
  expect(screen.queryByText('Updating…')).not.toBeInTheDocument()
})

it('shows a retryable error when rescoring after a chip change fails', async () => {
  const user = userEvent.setup()
  vi.spyOn(client, 'scoreItems').mockRejectedValue(new client.ApiError('network_error', 'offline', 0))
  render(<ResultsView result={makeResult('gemini')} onUpdate={() => {}} onScanAgain={() => {}} />)

  await user.click(screen.getByRole('radio', { name: 'Second-hand' }))

  expect(await screen.findByText("Can't reach EcoScan")).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
})

it('keeps the provider after the items are edited and recalculated', async () => {
  const user = userEvent.setup()
  vi.spyOn(client, 'getCarbonFactors').mockRejectedValue(new Error('not needed'))
  vi.spyOn(client, 'scoreItems').mockResolvedValue({ items: [makeItem()], total_carbon_kg: 5, total_saved_kg: 0, total_points: 0 })
  vi.spyOn(client, 'getOffers').mockResolvedValue({ points: 0, eligible: [], locked: [] })
  const onUpdate = vi.fn()
  render(<ResultsView result={makeResult('mock')} onUpdate={onUpdate} onScanAgain={() => {}} />)

  await user.click(screen.getByRole('button', { name: 'Edit items' }))
  await user.click(screen.getByRole('button', { name: 'Recalculate' }))

  expect(onUpdate).toHaveBeenCalledWith(expect.objectContaining({ provider: 'mock' }))
})
