import { describe, expect, it, vi } from 'vitest'

import { ApiError, analyzeImage, getCarbonFactors, getOffers, scoreItems } from './client'

/** Replace fetch with a mock that returns `body` (as JSON, or raw text) with `status`. */
function mockFetch(status: number, body: unknown, { raw = false } = {}) {
  const fetchMock = vi.fn(async () =>
    new Response(raw ? String(body) : JSON.stringify(body), {
      status,
      headers: { 'Content-Type': raw ? 'text/html' : 'application/json' },
    }),
  )
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

/** Run a call that should fail and return the ApiError it threw. */
async function apiErrorFrom(call: () => Promise<unknown>): Promise<ApiError> {
  const error = await call().catch((e: unknown) => e)
  expect(error).toBeInstanceOf(ApiError)
  return error as ApiError
}

describe('successful responses', () => {
  it('returns the parsed JSON body', async () => {
    mockFetch(200, { points: 120, eligible: [], locked: [] })

    await expect(getOffers(120)).resolves.toEqual({ points: 120, eligible: [], locked: [] })
  })

  it('calls the right URLs and methods', async () => {
    const fetchMock = mockFetch(200, {})

    await getOffers(95)
    await getCarbonFactors()
    await scoreItems([{ category: 'jeans', condition: 'second-hand' }])

    const calls = fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
    expect(calls[0][0]).toBe('/api/offers?points=95')
    expect(calls[1][0]).toBe('/api/carbon-factors')
    expect(calls[2][0]).toBe('/api/score')
    expect(calls[2][1]?.method).toBe('POST')
    expect(JSON.parse(String(calls[2][1]?.body))).toEqual({ items: [{ category: 'jeans', condition: 'second-hand' }] })
  })

  it('uploads the image as the multipart field "file"', async () => {
    const fetchMock = mockFetch(200, {})
    const file = new File(['x'], 'photo.png', { type: 'image/png' })

    await analyzeImage(file)

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(url).toBe('/api/analyze')
    expect(init.method).toBe('POST')
    expect((init.body as FormData).get('file')).toBe(file)
  })
})

describe('error responses', () => {
  it('turns the backend error body into an ApiError', async () => {
    mockFetch(413, { error: { code: 'image_too_large', message: 'The image is too large. The limit is 5 MB.' } })

    const error = await apiErrorFrom(() => analyzeImage(new File(['x'], 'p.png', { type: 'image/png' })))

    expect(error.code).toBe('image_too_large')
    expect(error.message).toBe('The image is too large. The limit is 5 MB.')
    expect(error.status).toBe(413)
  })

  it('keeps validation details', async () => {
    const details = [{ loc: ['body', 'items'], msg: 'List should have at least 1 item', type: 'too_short' }]
    mockFetch(422, { error: { code: 'validation_error', message: 'The request data is invalid.', details } })

    const error = await apiErrorFrom(() => scoreItems([]))

    expect(error.code).toBe('validation_error')
    expect(error.details).toEqual(details)
  })

  it('uses http_error when the error is not in our shape', async () => {
    mockFetch(502, '<html>Bad Gateway</html>', { raw: true })

    const error = await apiErrorFrom(() => getOffers(10))

    expect(error.code).toBe('http_error')
    expect(error.status).toBe(502)
  })

  it('uses http_error for JSON errors from outside our handlers', async () => {
    mockFetch(404, { detail: 'Not Found' })

    expect((await apiErrorFrom(() => getOffers(10))).code).toBe('http_error')
  })

  it('uses invalid_response when a success response is not JSON', async () => {
    mockFetch(200, 'not json', { raw: true })

    const error = await apiErrorFrom(() => getCarbonFactors())

    expect(error.code).toBe('invalid_response')
  })

  it('uses network_error with status 0 when the server cannot be reached', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new TypeError('Failed to fetch'))))

    const error = await apiErrorFrom(() => getOffers(10))

    expect(error.code).toBe('network_error')
    expect(error.status).toBe(0)
  })

  it('lets a cancelled request through as an AbortError, not an ApiError', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new DOMException('aborted', 'AbortError'))))

    const error = await analyzeImage(new File(['x'], 'p.png', { type: 'image/png' })).catch((e: unknown) => e)

    expect(error).not.toBeInstanceOf(ApiError)
    expect((error as DOMException).name).toBe('AbortError')
  })
})
