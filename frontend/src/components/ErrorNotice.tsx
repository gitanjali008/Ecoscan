import { describeError } from '../lib/errors'

type Action = { label: string; onClick: () => void }

type Props = {
  error: unknown
  /** Shown only when the error is one that a retry could fix. */
  onRetry?: () => void
  secondaryAction?: Action
}

export function ErrorNotice({ error, onRetry, secondaryAction }: Props) {
  const { title, message, retryable } = describeError(error)

  return (
    <div role="alert" className="rounded-3xl border border-clay/30 bg-clay/10 p-5">
      <p className="font-display text-lg font-semibold text-clay">{title}</p>
      <p className="mt-1 text-bark">{message}</p>
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        {retryable && onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="min-h-12 rounded-full bg-moss px-6 font-semibold text-linen hover:bg-moss-dark"
          >
            Try again
          </button>
        )}
        {secondaryAction && (
          <button
            type="button"
            onClick={secondaryAction.onClick}
            className="min-h-12 rounded-full border border-moss px-6 font-semibold text-moss hover:bg-moss/10"
          >
            {secondaryAction.label}
          </button>
        )}
      </div>
    </div>
  )
}
