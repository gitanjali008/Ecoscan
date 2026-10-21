export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <svg viewBox="0 0 32 32" className="size-8" aria-hidden="true">
        <rect width="32" height="32" rx="8" className="fill-moss" />
        <path
          d="M9 23c0-8 5-13 14-14-1 9-6 14-14 14Zm0 0 7-7"
          fill="none"
          className="stroke-linen"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span className="font-display text-xl font-semibold tracking-tight text-moss">EcoScan</span>
    </div>
  )
}
