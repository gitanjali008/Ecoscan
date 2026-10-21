import { useState } from 'react'

import { analyzeImage, ApiError } from '../api/client'
import type { AnalysisResponse } from '../api/types'
import { validateImageFile } from '../lib/imageFile'
import { ImagePreview } from './ImagePreview'
import { PhotoPicker } from './PhotoPicker'

type Props = {
  onResult: (result: AnalysisResponse) => void
}

export function ScanPanel({ onResult }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [scanning, setScanning] = useState(false)

  function select(candidate: File) {
    const problem = validateImageFile(candidate)
    setError(problem)
    setFile(problem ? null : candidate)
  }

  async function scan() {
    if (!file) return
    setScanning(true)
    setError(null)
    try {
      onResult(await analyzeImage(file))
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setScanning(false)
    }
  }

  return (
    <section aria-label="Scan your clothes" className="space-y-4">
      {file ? (
        <>
          <ImagePreview file={file} onChange={() => setFile(null)} disabled={scanning} />
          <button
            type="button"
            onClick={scan}
            disabled={scanning}
            className="min-h-14 w-full rounded-full bg-moss text-lg font-semibold text-linen hover:bg-moss-dark disabled:opacity-60"
          >
            {scanning ? 'Scanning…' : 'Scan'}
          </button>
        </>
      ) : (
        <PhotoPicker onSelect={select} />
      )}

      {error && (
        <p role="alert" className="rounded-2xl bg-clay/10 p-4 text-clay">
          {error}
        </p>
      )}
    </section>
  )
}
