import { beforeEach, describe, expect, it, vi } from 'vitest'

import { makeFile } from '../test/fixtures'
import { fitWithin, JPEG_QUALITY, MAX_SIDE_PX, resizeImage, UnsupportedImageError } from './resizeImage'

describe('fitWithin', () => {
  it('scales the longest side down to the limit and keeps the aspect ratio', () => {
    expect(fitWithin(4032, 3024)).toEqual({ width: 1600, height: 1200 })
    expect(fitWithin(3024, 4032)).toEqual({ width: 1200, height: 1600 })
  })

  it('never scales up', () => {
    expect(fitWithin(800, 600)).toEqual({ width: 800, height: 600 })
    expect(fitWithin(MAX_SIDE_PX, 900)).toEqual({ width: MAX_SIDE_PX, height: 900 })
  })
})

// jsdom cannot decode images or draw on a canvas, so both are faked here.
describe('resizeImage', () => {
  let toBlobArgs: unknown[]

  beforeEach(() => {
    vi.spyOn(document, 'createElement')
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ drawImage: vi.fn() } as never)
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((callback, ...args) => {
      toBlobArgs = args
      callback(new Blob(['jpeg bytes'], { type: 'image/jpeg' }))
    })
  })

  function lastCanvas() {
    return vi.mocked(document.createElement).mock.results.at(-1)!.value as HTMLCanvasElement
  }

  function stubBitmap(width: number, height: number) {
    const close = vi.fn()
    const create = vi.fn().mockResolvedValue({ width, height, close })
    vi.stubGlobal('createImageBitmap', create)
    return { create, close }
  }

  it('returns a JPEG no larger than the limit, applying EXIF orientation', async () => {
    const { create, close } = stubBitmap(4032, 3024)

    const result = await resizeImage(makeFile('IMG_0001.HEIC', 'image/heic', 1000))

    expect(result.type).toBe('image/jpeg')
    expect(result.name).toBe('IMG_0001.jpg')
    expect(lastCanvas()).toMatchObject({ width: 1600, height: 1200 })
    expect(toBlobArgs).toEqual(['image/jpeg', JPEG_QUALITY])
    expect(create).toHaveBeenCalledWith(expect.any(File), { imageOrientation: 'from-image' })
    expect(close).toHaveBeenCalled()
  })

  it('does not upscale a small photo', async () => {
    stubBitmap(640, 480)

    await resizeImage(makeFile('small.png', 'image/png', 1000))

    expect(lastCanvas()).toMatchObject({ width: 640, height: 480 })
  })

  it('throws UnsupportedImageError when the browser cannot decode the file', async () => {
    vi.stubGlobal('createImageBitmap', vi.fn().mockRejectedValue(new DOMException('bad', 'InvalidStateError')))
    vi.stubGlobal('URL', { ...URL, createObjectURL: () => 'blob:x', revokeObjectURL: vi.fn() })
    // The <img> fallback fails too.
    vi.stubGlobal(
      'Image',
      class {
        onerror: (() => void) | null = null
        set src(_: string) {
          setTimeout(() => this.onerror?.())
        }
      },
    )

    await expect(resizeImage(makeFile('photo.heic', 'image/heic', 1000))).rejects.toBeInstanceOf(
      UnsupportedImageError,
    )
  })
})
