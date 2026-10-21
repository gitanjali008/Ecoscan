import { useEffect } from 'react'

type Props = {
  message: string
  /** Pass a stable function (e.g. from useCallback): a new one restarts the timer. */
  onClose: () => void
  durationMs?: number
}

/** A short confirmation at the bottom of the screen that disappears by itself. */
export function Toast({ message, onClose, durationMs = 4000 }: Props) {
  useEffect(() => {
    const timer = setTimeout(onClose, durationMs)
    return () => clearTimeout(timer)
  }, [onClose, durationMs])

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-0 z-10 flex justify-center px-4 pb-[max(1rem,env(safe-area-inset-bottom))]">
      <div
        role="status"
        className="pointer-events-auto flex w-full max-w-md items-start gap-3 rounded-2xl bg-bark p-4 text-linen shadow-lg"
      >
        <p className="flex-1">{message}</p>
        <button
          type="button"
          onClick={onClose}
          aria-label="Dismiss"
          className="-m-1 rounded-full p-1 text-linen/70 hover:text-linen"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
