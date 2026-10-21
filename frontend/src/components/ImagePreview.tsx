import { useMemo } from 'react'

import { formatMb } from '../lib/imageFile'

type Props = {
  file: File
  onChange: () => void
  disabled?: boolean
}

export function ImagePreview({ file, onChange, disabled = false }: Props) {
  // A temporary URL for the chosen file. It is released once the image has loaded:
  // the browser keeps showing the decoded picture.
  const url = useMemo(() => URL.createObjectURL(file), [file])

  return (
    <figure className="overflow-hidden rounded-3xl border border-sand bg-white/60">
      <div className="flex aspect-[4/3] items-center justify-center bg-sand/60">
        <img
          src={url}
          alt="The photo you chose"
          onLoad={() => URL.revokeObjectURL(url)}
          className="size-full object-contain"
        />
      </div>
      <figcaption className="flex items-center justify-between gap-3 p-4">
        <span className="min-w-0 truncate text-sm text-stone">
          {file.name} · {formatMb(file.size)} MB
        </span>
        <button
          type="button"
          onClick={onChange}
          disabled={disabled}
          className="shrink-0 text-sm font-semibold text-moss underline-offset-4 hover:underline disabled:opacity-50"
        >
          Change photo
        </button>
      </figcaption>
    </figure>
  )
}
