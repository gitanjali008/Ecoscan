import { useEffect, useState } from 'react'

const MESSAGES = ['Spotting each item…', 'Checking materials…', 'Working out the carbon…']

export function ScanningIndicator({ onCancel }: { onCancel: () => void }) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setStep((s) => (s + 1) % MESSAGES.length), 2500)
    return () => clearInterval(timer)
  }, [])

  return (
    <div role="status" className="flex items-center gap-4 rounded-3xl border border-sand bg-white/60 p-5">
      <span
        aria-hidden="true"
        className="size-8 shrink-0 animate-spin rounded-full border-4 border-fern/30 border-t-moss"
      />
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{MESSAGES[step]}</p>
        <p className="text-sm text-stone">This usually takes a few seconds.</p>
      </div>
      <button type="button" onClick={onCancel} className="shrink-0 text-sm font-semibold text-moss hover:underline">
        Cancel
      </button>
    </div>
  )
}
