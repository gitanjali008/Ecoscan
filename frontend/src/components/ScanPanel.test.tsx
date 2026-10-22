import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'

import { resizeImage, UnsupportedImageError } from '../lib/resizeImage'
import { makeFile } from '../test/fixtures'
import { ScanPanel } from './ScanPanel'

vi.mock('../lib/resizeImage', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../lib/resizeImage')>()),
  resizeImage: vi.fn(),
}))

beforeEach(() => {
  vi.stubGlobal('URL', { ...URL, createObjectURL: () => 'blob:preview', revokeObjectURL: vi.fn() })
})

function choosePhoto(file: File) {
  const { container } = render(<ScanPanel onResult={vi.fn()} />)
  const input = container.querySelector<HTMLInputElement>('input[type="file"]:not([capture])')!
  return userEvent.upload(input, file)
}

it('shows "Preparing photo…" while resizing, then the resized preview', async () => {
  let finish!: (file: File) => void
  vi.mocked(resizeImage).mockReturnValue(new Promise((resolve) => (finish = resolve)))

  await choosePhoto(makeFile('IMG_0001.HEIC', 'image/heic', 1000))
  expect(screen.getByRole('status')).toHaveTextContent('Preparing photo…')

  finish(makeFile('IMG_0001.jpg', 'image/jpeg', 300 * 1024))

  expect(await screen.findByText(/IMG_0001\.jpg · 0\.3 MB/)).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Scan' })).toBeInTheDocument()
})

it('shows a friendly message when the browser cannot decode the photo', async () => {
  vi.mocked(resizeImage).mockRejectedValue(new UnsupportedImageError())

  await choosePhoto(makeFile('IMG_0001.HEIC', 'image/heic', 1000))

  expect(await screen.findByRole('alert')).toHaveTextContent(
    "This photo format isn't supported here. Please convert it to JPG or PNG.",
  )
  expect(screen.queryByRole('button', { name: 'Scan' })).not.toBeInTheDocument()
})
