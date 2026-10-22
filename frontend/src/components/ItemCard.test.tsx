import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'

import { makeItem } from '../test/fixtures'
import { ItemCard } from './ItemCard'

it('uses the scan label as the title and still shows the category and material', () => {
  render(<ItemCard item={makeItem({ category: 'dress', material: 'polyester', label: 'red floral midi dress' })} />)

  expect(screen.getByRole('heading')).toHaveTextContent('Red floral midi dress')
  expect(screen.getByText('Dress · Polyester')).toBeInTheDocument()
})

it('falls back to the category when there is no label', () => {
  render(<ItemCard item={makeItem({ category: 'jeans', material: 'cotton', label: null })} />)

  expect(screen.getByRole('heading')).toHaveTextContent('Jeans')
  expect(screen.getByText('Cotton')).toBeInTheDocument()
})

it('shows the eco tip', () => {
  render(<ItemCard item={makeItem({ tip: 'Great choice! Buying it second-hand saved about 8 kg of CO2.' })} />)

  expect(screen.getByText('Great choice! Buying it second-hand saved about 8 kg of CO2.')).toBeInTheDocument()
})
