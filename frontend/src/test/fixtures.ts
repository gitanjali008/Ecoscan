import type { LockedOffer, Offer, ScoredItem } from '../api/types'

export function makeFile(name: string, type: string, sizeBytes: number): File {
  return new File([new Uint8Array(sizeBytes)], name, { type })
}

export function makeItem(overrides: Partial<ScoredItem> = {}): ScoredItem {
  return {
    category: 't-shirt',
    material: 'cotton',
    condition: 'new',
    confidence: 0.9,
    label: null,
    baseline_kg: 5,
    actual_kg: 5,
    saved_kg: 0,
    points: 0,
    tip: 'Bought second-hand, this would save 4 kg CO2 (+40 pts). Organic cotton would save about 1.5 kg.',
    ...overrides,
  }
}

export function makeOffer(overrides: Partial<Offer> = {}): Offer {
  return {
    id: 'swap-pass',
    title: 'Free clothing swap entry',
    partner: 'Swap Circle',
    description: 'One free ticket to a local clothing swap event.',
    points_required: 30,
    ...overrides,
  }
}

export function makeLockedOffer(overrides: Partial<LockedOffer> = {}): LockedOffer {
  return {
    ...makeOffer({ id: 'plant-tree', title: 'Plant a tree', partner: 'Green Roots', points_required: 150 }),
    points_needed: 18,
    ...overrides,
  }
}
