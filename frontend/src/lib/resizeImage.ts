// Shrinks a photo in the browser before upload: phone photos are often 5–15 MB,
// but the scan only needs a modest size. The result is always a JPEG, so any
// format the browser can decode (HEIC on Safari, GIF, BMP…) can be scanned.

export const MAX_SIDE_PX = 1600
export const JPEG_QUALITY = 0.85

/** The browser could not decode the file (e.g. HEIC on Windows Chrome). */
export class UnsupportedImageError extends Error {
  constructor() {
    super("This photo format isn't supported here. Please convert it to JPG or PNG.")
    this.name = 'UnsupportedImageError'
  }
}

/** Scale so the longest side is at most maxSide. Never scales up; keeps the aspect ratio. */
export function fitWithin(width: number, height: number, maxSide = MAX_SIDE_PX) {
  const scale = Math.min(1, maxSide / Math.max(width, height))
  return {
    width: Math.max(1, Math.round(width * scale)),
    height: Math.max(1, Math.round(height * scale)),
  }
}

type Decoded = { source: CanvasImageSource; width: number; height: number; release: () => void }

function decodeWithImg(file: File): Promise<Decoded> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () =>
      resolve({
        source: img,
        width: img.naturalWidth,
        height: img.naturalHeight,
        release: () => URL.revokeObjectURL(url),
      })
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new UnsupportedImageError())
    }
    img.src = url
  })
}

// Both paths apply the EXIF orientation, so a portrait phone photo stays upright:
// createImageBitmap is told to, and <img> does it by default in current browsers.
async function decode(file: File): Promise<Decoded> {
  if (typeof createImageBitmap === 'function') {
    try {
      const bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' })
      return { source: bitmap, width: bitmap.width, height: bitmap.height, release: () => bitmap.close() }
    } catch {
      // Some browsers decode more formats in <img> than in createImageBitmap.
    }
  }
  return decodeWithImg(file)
}

/** A JPEG copy of the photo, at most MAX_SIDE_PX on its longest side. */
export async function resizeImage(file: File): Promise<File> {
  const image = await decode(file)
  try {
    const { width, height } = fitWithin(image.width, image.height)
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const context = canvas.getContext('2d')
    if (!context) throw new Error('Canvas is not available.')
    context.drawImage(image.source, 0, 0, width, height)

    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY))
    if (!blob) throw new Error('The photo could not be converted.')

    const name = `${file.name.replace(/\.[^.]*$/, '') || 'photo'}.jpg`
    return new File([blob], name, { type: 'image/jpeg' })
  } finally {
    image.release()
  }
}
