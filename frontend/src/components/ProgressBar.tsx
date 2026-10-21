type Props = {
  value: number
  max: number
  label: string
}

export function ProgressBar({ value, max, label }: Props) {
  const percent = max > 0 ? Math.min(Math.max(value / max, 0), 1) * 100 : 0

  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={Math.min(value, max)}
      className="h-2.5 overflow-hidden rounded-full bg-sand/70"
    >
      <div className="h-full rounded-full bg-ochre" style={{ width: `${percent}%` }} />
    </div>
  )
}
