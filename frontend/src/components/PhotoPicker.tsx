import { useRef, useState, type ChangeEvent, type DragEvent } from 'react'

import { CameraModal } from './CameraModal'
import { CameraIcon, PhotoIcon } from './icons'

type Props = {
  onSelect: (file: File) => void
}

/** Phones get the native camera (input capture); desktops get a webcam modal when available. */
function shouldUseWebcamModal(): boolean {
  const isTouchFirst = window.matchMedia('(pointer: coarse)').matches
  return !isTouchFirst && typeof navigator.mediaDevices?.getUserMedia === 'function'
}

export function PhotoPicker({ onSelect }: Props) {
  const fileInput = useRef<HTMLInputElement>(null)
  const cameraInput = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [cameraOpen, setCameraOpen] = useState(false)

  function handleInput(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    // Reset so choosing the same file again still fires a change.
    event.target.value = ''
    if (file) onSelect(file)
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault()
    setDragging(false)
    const file = event.dataTransfer.files[0]
    if (file) onSelect(file)
  }

  function takePhoto() {
    if (shouldUseWebcamModal()) setCameraOpen(true)
    else cameraInput.current?.click()
  }

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`rounded-3xl border-2 border-dashed p-6 text-center transition-colors sm:p-10 ${
        dragging ? 'border-moss bg-fern/15' : 'border-sand bg-white/50'
      }`}
    >
      <PhotoIcon className="mx-auto size-10 text-fern" />
      <p className="mt-3 font-display text-xl font-semibold">Add a photo of your clothes</p>
      <p className="mt-1 hidden text-stone sm:block">Drag it here, or use the buttons below.</p>
      <p className="mt-1 text-stone sm:hidden">One outfit or a few items laid out works best.</p>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
        <button
          type="button"
          onClick={takePhoto}
          className="inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-moss px-6 font-semibold text-linen hover:bg-moss-dark"
        >
          <CameraIcon />
          Take photo
        </button>
        <button
          type="button"
          onClick={() => fileInput.current?.click()}
          className="inline-flex min-h-12 items-center justify-center gap-2 rounded-full border border-moss px-6 font-semibold text-moss hover:bg-moss/10"
        >
          <PhotoIcon />
          Choose photo
        </button>
      </div>

      <input ref={fileInput} type="file" accept="image/*" hidden onChange={handleInput} />
      <input ref={cameraInput} type="file" accept="image/*" capture="environment" hidden onChange={handleInput} />

      {cameraOpen && (
        <CameraModal
          onClose={() => setCameraOpen(false)}
          onCapture={(file) => {
            setCameraOpen(false)
            onSelect(file)
          }}
        />
      )}
    </div>
  )
}
