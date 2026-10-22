// Client-side checks so a wrong file is caught before it is uploaded.
// The backend still validates everything.

/**
 * Sanity cap on the photo the user picks. It is resized before upload, so this
 * only stops files far too big to decode comfortably on a phone.
 */
export const MAX_ORIGINAL_MB = 30

/** Keep in sync with MAX_IMAGE_MB in backend/.env. Checked on the resized JPEG. */
export const MAX_UPLOAD_MB = 10

const MB = 1024 * 1024

export function formatMb(bytes: number): string {
  return (bytes / MB).toFixed(1)
}

/** A friendly message if the chosen file cannot be used, otherwise null. */
export function checkOriginalFile(file: File): string | null {
  // Some systems send no type for formats they don't know (e.g. HEIC on Windows):
  // let the browser try to decode those instead of rejecting them here.
  if (file.type && !file.type.startsWith('image/')) {
    return `"${file.name}" isn't a photo. Please choose an image file.`
  }
  if (file.size === 0) {
    return 'That file is empty. Please choose another photo.'
  }
  if (file.size > MAX_ORIGINAL_MB * MB) {
    return `This photo is ${formatMb(file.size)} MB. Please choose one under ${MAX_ORIGINAL_MB} MB.`
  }
  return null
}

/** A friendly message if the resized photo is still too large to upload, otherwise null. */
export function checkUploadFile(file: File): string | null {
  if (file.size > MAX_UPLOAD_MB * MB) {
    return `This photo is still ${formatMb(file.size)} MB after resizing. Please choose a smaller one.`
  }
  return null
}
