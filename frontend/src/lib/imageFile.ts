// Client-side checks that mirror the backend's, so a wrong file is caught
// before it is uploaded. The backend still validates everything.

export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

/** Keep in sync with MAX_IMAGE_MB in backend/.env. */
export const MAX_IMAGE_MB = 5

const MAX_IMAGE_BYTES = MAX_IMAGE_MB * 1024 * 1024

export function formatMb(bytes: number): string {
  return (bytes / (1024 * 1024)).toFixed(1)
}

/** A friendly message if the file cannot be scanned, otherwise null. */
export function validateImageFile(file: File): string | null {
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
    return `"${file.name}" isn't a photo we can scan. Please use a JPEG, PNG or WebP image.`
  }
  if (file.size === 0) {
    return 'That file is empty. Please choose another photo.'
  }
  if (file.size > MAX_IMAGE_BYTES) {
    return `This photo is ${formatMb(file.size)} MB. Please choose one under ${MAX_IMAGE_MB} MB.`
  }
  return null
}
