import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'

import { makeItem } from '../test/fixtures'
import { ResultsSummary } from './ResultsSummary'

it('shows the total carbon, CO2 saved and points', () => {
  render(
    <ResultsSummary
      result={{ items: [makeItem()], total_carbon_kg: 24.4, total_saved_kg: 13.2, total_points: 132 }}
    />,
  )

  expect(screen.getByText('Carbon footprint').nextElementSibling).toHaveTextContent('24.4 kg')
  expect(screen.getByText('CO2 saved').nextElementSibling).toHaveTextContent('13.2 kg')
  expect(screen.getByText('Points').nextElementSibling).toHaveTextContent('132')
})

it('rounds kg to one decimal and drops a trailing .0', () => {
  render(<ResultsSummary result={{ items: [], total_carbon_kg: 5, total_saved_kg: 1.25, total_points: 13 }} />)

  expect(screen.getByText('5 kg')).toBeInTheDocument()
  expect(screen.getByText('1.3 kg')).toBeInTheDocument()
})
