import { describe, expect, it } from 'vitest'

import { makeFile } from '../test/fixtures'
import { MAX_ORIGINAL_MB, MAX_UPLOAD_MB, checkOriginalFile, checkUploadFile } from './imageFile'

const MB = 1024 * 1024

describe('checkOriginalFile', () => {
  it.each(['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/gif', 'image/bmp'])(
    'accepts %s',
    (type) => {
      expect(checkOriginalFile(makeFile('photo', type, 1000))).toBeNull()
    },
  )

  it('lets a file with no type through, so the browser can try to decode it', () => {
    expect(checkOriginalFile(makeFile('photo.heic', '', 1000))).toBeNull()
  })

  it.each([
    ['notes.pdf', 'application/pdf'],
    ['clip.mp4', 'video/mp4'],
  ])('rejects %s with a friendly message', (name, type) => {
    const message = checkOriginalFile(makeFile(name, type, 1000))

    expect(message).toContain(name)
    expect(message).toMatch(/isn't a photo/)
  })

  it('rejects an empty file', () => {
    expect(checkOriginalFile(makeFile('photo.jpg', 'image/jpeg', 0))).toMatch(/empty/i)
  })

  it('accepts a large phone photo well over the upload limit', () => {
    expect(checkOriginalFile(makeFile('photo.jpg', 'image/jpeg', 12 * MB))).toBeNull()
  })

  it('rejects an original over the sanity cap and says how big it is', () => {
    const message = checkOriginalFile(makeFile('photo.jpg', 'image/jpeg', MAX_ORIGINAL_MB * MB + 1))

    expect(message).toContain('30.0 MB')
    expect(message).toContain(`under ${MAX_ORIGINAL_MB} MB`)
  })
})

describe('checkUploadFile', () => {
  it('accepts a file exactly at the upload limit', () => {
    expect(checkUploadFile(makeFile('photo.jpg', 'image/jpeg', MAX_UPLOAD_MB * MB))).toBeNull()
  })

  it('rejects a resized file over the upload limit', () => {
    expect(checkUploadFile(makeFile('photo.jpg', 'image/jpeg', MAX_UPLOAD_MB * MB + 1))).toMatch(/after resizing/)
  })
})
