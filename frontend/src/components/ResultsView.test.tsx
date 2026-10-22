import { render, screen } from '@testing-library/react'
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
