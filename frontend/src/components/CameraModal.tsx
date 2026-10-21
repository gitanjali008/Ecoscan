import { useEffect, useRef, useState } from 'react'

type Props = {
  onCapture: (file: File) => void
  onClose: () => void
}

function cameraErrorMessage(error: unknown): string {
  const name = error instanceof DOMException ? error.name : ''
  if (name === 'NotAllowedError' || name === 'SecurityError') {
    return 'Camera access was blocked. Allow it in your browser settings, or choose a photo instead.'
  }
  if (name === 'NotFoundError' || name === 'OverconstrainedError') {
    return 'No camera was found on this device. Choose a photo instead.'
  }
  if (name === 'NotReadableError') {
    return 'The camera is being used by another app. Close it and try again.'
  }
  return 'The camera could not be opened. Choose a photo instead.'
}

/** Desktop webcam capture. Mount it to open; unmounting turns the camera off. */
export function CameraModal({ onCapture, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (dialog && !dialog.open) dialog.showModal()

    let stream: MediaStream | null = null
    let cancelled = false
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: 'environment' }, audio: false })
      .then((s) => {
        if (cancelled) {
          s.getTracks().forEach((track) => track.stop())
          return
        }
        stream = s
        if (videoRef.current) videoRef.current.srcObject = s
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(cameraErrorMessage(e))
      })

    return () => {
      cancelled = true
      stream?.getTracks().forEach((track) => track.stop())
    }
  }, [])

  function capture() {
    const video = videoRef.current
    if (!video || !video.videoWidth) return
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d')?.drawImage(video, 0, 0)
    canvas.toBlob(
      (blob) => {
        if (blob) onCapture(new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' }))
      },
      'image/jpeg',
      0.9,
    )
  }

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="camera-title"
      // Esc closes the dialog: let the parent unmount it so the camera stops.
      onCancel={(event) => {
        event.preventDefault()
        onClose()
      }}
      className="m-auto w-[min(36rem,calc(100%-2rem))] rounded-3xl bg-linen p-5 text-bark backdrop:bg-bark/60"
    >
      <h2 id="camera-title" className="font-display text-xl font-semibold">
        Take a photo
      </h2>

      {error ? (
        <p role="alert" className="mt-4 rounded-2xl bg-clay/10 p-4 text-clay">
          {error}
        </p>
      ) : (
        <div className="mt-4 aspect-[4/3] overflow-hidden rounded-2xl bg-bark">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            onLoadedMetadata={() => setReady(true)}
            className="size-full object-cover"
          />
        </div>
      )}

      <div className="mt-5 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={onClose}
          className="min-h-12 rounded-full border border-sand px-5 font-semibold text-bark hover:bg-sand/50"
        >
          Cancel
        </button>
        {!error && (
          <button
            type="button"
            onClick={capture}
            disabled={!ready}
            className="min-h-12 rounded-full bg-moss px-6 font-semibold text-linen hover:bg-moss-dark disabled:opacity-50"
          >
            {ready ? 'Capture' : 'Starting camera…'}
          </button>
        )}
      </div>
    </dialog>
  )
}
