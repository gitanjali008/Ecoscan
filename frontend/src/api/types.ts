// TypeScript versions of the backend's Pydantic schemas (backend/app/schemas.py).
// Keep the two in sync: field names match the JSON the API sends and receives.

export type Condition = 'new' | 'second-hand'

/** One clothing item as the API returns it (all fields filled in). */
export interface DetectedItem {
  category: string
  material: string
  condition: Condition
  confidence: number
  /** Short description from the scan, e.g. "red floral midi dress" */
  label: string | null
}

/** An item sent to the API. Only category is required; the backend fills in the rest. */
export type ItemInput = Pick<DetectedItem, 'category'> & Partial<Omit<DetectedItem, 'category'>>

export interface ScoredItem extends DetectedItem {
  /** kg CO2e of the same item bought new, in a conventional material */
  baseline_kg: number
  /** kg CO2e after material and condition adjustments */
  actual_kg: number
  /** baseline_kg - actual_kg, never below 0 */
  saved_kg: number
  points: number
  /** One short, friendly eco tip for this item */
  tip: string
}

export interface ScoreRequest {
  items: ItemInput[]
}

export interface ScoreResponse {
  items: ScoredItem[]
  total_carbon_kg: number
  total_saved_kg: number
  total_points: number
}

export interface Offer {
  id: string
  title: string
  partner: string
  description: string
  points_required: number
}

export interface LockedOffer extends Offer {
  /** How many more points unlock this offer */
  points_needed: number
}

export interface OffersResponse {
  points: number
  eligible: Offer[]
  locked: LockedOffer[]
}

/** Everything the UI needs after one scan. */
export interface AnalysisResponse extends ScoreResponse {
  offers: OffersResponse
  /** The vision provider that read the photo: "mock" means sample results */
  provider: string
}

export interface CarbonFactorsResponse {
  base_kg: Record<string, number>
  default_kg: number
  material_factor: Record<string, number>
  condition_factor: Record<string, number>
}

/** Codes the backend sends, plus the ones the client adds when there is no backend answer. */
export type ErrorCode =
  | 'empty_image'
  | 'image_too_large'
  | 'invalid_image'
  | 'no_clothing_detected'
  | 'vision_service_error'
  | 'validation_error'
  | 'network_error' // client: the server could not be reached
  | 'http_error' // client: an error response without our JSON shape (e.g. a proxy page)
  | 'invalid_response' // client: a success response that was not valid JSON
  | (string & {}) // future backend codes still type-check

/** One entry of a validation error's details (FastAPI / Pydantic format). */
export interface ValidationIssue {
  loc: (string | number)[]
  msg: string
  type: string
}

/** The shape of every error the backend returns. */
export interface ApiErrorBody {
  error: {
    code: ErrorCode
    message: string
    details?: ValidationIssue[]
  }
}
