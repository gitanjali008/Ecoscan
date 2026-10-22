import { getOffers, scoreItems } from './client'
import type { AnalysisResponse, DetectedItem, ItemInput } from './types'

/** What the API needs to score an item again: what was detected, not the old results. */
export function toItemInput({ category, material, condition, confidence, label }: DetectedItem): ItemInput {
  return { category, material, condition, confidence, label }
}

/**
 * Scores the items again and fetches the offers for the new points.
 * The photo is not read again, so the caller keeps the original provider.
 */
export async function rescore(items: ItemInput[]): Promise<Omit<AnalysisResponse, 'provider'>> {
  const score = await scoreItems(items)
  const offers = await getOffers(score.total_points)
  return { ...score, offers }
}
