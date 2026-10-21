import { useRef, useState } from 'react'

import { analyzeImage } from '../api/client'
import type { AnalysisResponse } from '../api/types'
import { validateImageFile } from '../lib/imageFile'
import { ErrorNotice } from './ErrorNotice'
import { ImagePreview } from './ImagePreview'
import { PhotoPicker } from './PhotoPicker'
import { ScanningIndicator } from './ScanningIndicator'

type Props = {
  onResult: (result: AnalysisResponse) => void
}

export function ScanPanel({ onResult }: Props) {
  const [file, setFile] = useState<File | null>(null)
  // A file rejected before upload (wrong type, too large).
  const [fileProblem, setFileProblem] = useState<string | null>(null)
  // An error from the scan itself.
  const [scanError, setScanError] = useState<unknown>(null)
  const [scanning, setScanning] = useState(false)
  const controller = useRef<AbortController | null>(null)

  function select(candidate: File) {
    const problem = validateImageFile(candidate)
    setFileProblem(problem)
    setScanError(null)
    setFile(problem ? null : candidate)
  }

  function chooseAnother() {
    setFile(null)
    setScanError(null)
  }

  async function scan() {
    if (!file) return
    controller.current = new AbortController()
    setScanning(true)
    setScanError(null)
    try {
      onResult(await analyzeImage(file, controller.current.signal))
    } catch (e) {
      // Cancelled by the user: just go back to the preview.
      if (!(e instanceof DOMException && e.name === 'AbortError')) setScanError(e)
    } finally {
      setScanning(false)
    }
  }

  if (!file) {
    return (
      <section aria-label="Scan your clothes" className="space-y-4">
        <PhotoPicker onSelect={select} />
        {fileProblem && (
          <p role="alert" className="rounded-2xl bg-clay/10 p-4 text-clay">
            {fileProblem}
          </p>
        )}
      </section>
    )
  }

  return (
    <section aria-label="Scan your clothes" className="space-y-4">
      <ImagePreview file={file} onChange={chooseAnother} disabled={scanning} />

      {scanning ? (
        <ScanningIndicator onCancel={() => controller.current?.abort()} />
      ) : scanError ? (
        <ErrorNotice
          error={scanError}
          onRetry={scan}
          secondaryAction={{ label: 'Choose another photo', onClick: chooseAnother }}
        />
      ) : (
        <button
          type="button"
          onClick={scan}
          className="min-h-14 w-full rounded-full bg-moss text-lg font-semibold text-linen hover:bg-moss-dark"
        >
          Scan
        </button>
      )}
    </section>
  )
}
