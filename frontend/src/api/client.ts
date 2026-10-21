// The only place the app talks to the backend. Every function either returns
// the typed response or throws an ApiError, so components handle one error type.

import { API_BASE } from './config'
import type {
  AnalysisResponse,
  ApiErrorBody,
  CarbonFactorsResponse,
  ErrorCode,
  ItemInput,
  OffersResponse,
  ScoreRequest,
  ScoreResponse,
  ValidationIssue,
} from './types'

export class ApiError extends Error {
  readonly code: ErrorCode
  /** HTTP status, or 0 when the server could not be reached */
  readonly status: number
  readonly details?: ValidationIssue[]

  constructor(code: ErrorCode, message: string, status: number, details?: ValidationIssue[]) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }
}

function isApiErrorBody(body: unknown): body is ApiErrorBody {
  if (typeof body !== 'object' || body === null || !('error' in body)) return false
  const error = (body as { error: unknown }).error
  return (
    typeof error === 'object' &&
    error !== null &&
    typeof (error as { code?: unknown }).code === 'string' &&
    typeof (error as { message?: unknown }).message === 'string'
  )
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, init)
  } catch (cause) {
    // A cancelled request is not a failure: let the caller see the AbortError.
    if (cause instanceof DOMException && cause.name === 'AbortError') throw cause
    throw new ApiError('network_error', 'Could not reach the EcoScan server. Check your connection and try again.', 0)
  }

  const body: unknown = await response.json().catch(() => undefined)

  if (!response.ok) {
    if (isApiErrorBody(body)) {
      const { code, message, details } = body.error
      throw new ApiError(code, message, response.status, details)
    }
    throw new ApiError('http_error', `The server returned an unexpected error (${response.status}).`, response.status)
  }

  if (body === undefined) {
    throw new ApiError('invalid_response', 'The server sent a response the app could not read.', response.status)
  }
  return body as T
}

/** Upload a photo and get detected items, their carbon and points, totals and offers. */
export function analyzeImage(file: File, signal?: AbortSignal): Promise<AnalysisResponse> {
  const form = new FormData()
  form.append('file', file)
  // No Content-Type header: the browser sets multipart/form-data with its boundary.
  return request<AnalysisResponse>('/analyze', { method: 'POST', body: form, signal })
}

/** Recalculate carbon and points for items the user has edited. */
export function scoreItems(items: ItemInput[]): Promise<ScoreResponse> {
  const payload: ScoreRequest = { items }
  return request<ScoreResponse>('/score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

/** Offers the user can redeem now, and how far they are from the rest. */
export function getOffers(points: number): Promise<OffersResponse> {
  const query = new URLSearchParams({ points: String(points) })
  return request<OffersResponse>(`/offers?${query}`)
}

/** The carbon assumptions behind every score. */
export function getCarbonFactors(): Promise<CarbonFactorsResponse> {
  return request<CarbonFactorsResponse>('/carbon-factors')
}
