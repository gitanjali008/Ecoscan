import { describe, expect, it } from 'vitest'

import { makeFile } from '../test/fixtures'
import { MAX_IMAGE_MB, validateImageFile } from './imageFile'

const MB = 1024 * 1024

describe('validateImageFile', () => {
  it.each(['image/jpeg', 'image/png', 'image/webp'])('accepts %s', (type) => {
    expect(validateImageFile(makeFile('photo', type, 1000))).toBeNull()
  })

  it.each([
    ['notes.pdf', 'application/pdf'],
    ['photo.heic', 'image/heic'],
    ['anim.gif', 'image/gif'],
    ['mystery', ''],
  ])('rejects %s with a friendly message', (name, type) => {
    const message = validateImageFile(makeFile(name, type, 1000))

    expect(message).toContain(name)
    expect(message).toContain('JPEG, PNG or WebP')
  })

  it('rejects an empty file', () => {
    expect(validateImageFile(makeFile('photo.jpg', 'image/jpeg', 0))).toMatch(/empty/i)
  })

  it('accepts a file exactly at the size limit', () => {
    expect(validateImageFile(makeFile('photo.jpg', 'image/jpeg', MAX_IMAGE_MB * MB))).toBeNull()
  })

  it('rejects a file over the limit and says how big it is', () => {
    const message = validateImageFile(makeFile('photo.jpg', 'image/jpeg', MAX_IMAGE_MB * MB + 1))

    expect(message).toContain('5.0 MB')
    expect(message).toContain(`under ${MAX_IMAGE_MB} MB`)
  })
})
