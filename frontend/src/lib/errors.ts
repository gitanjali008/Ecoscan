import { ApiError } from '../api/client'

export type ErrorCopy = {
  title: string
  message: string
  /** Whether sending the same request again could work. */
  retryable: boolean
}

/** User-facing wording for any error the API client can throw. */
export function describeError(error: unknown): ErrorCopy {
  const code = error instanceof ApiError ? error.code : 'unknown'

  switch (code) {
    case 'invalid_image':
    case 'empty_image':
      return {
        title: "We can't read that file",
        message: 'Please choose a JPEG, PNG or WebP photo.',
        retryable: false,
      }
    case 'image_too_large':
      return {
        title: 'That photo is too large',
        message: `${(error as ApiError).message} Try a smaller photo.`,
        retryable: false,
      }
    case 'no_clothing_detected':
      return {
        title: "We couldn't spot any clothes",
        message: 'Try a well-lit photo where the clothes are clearly visible, worn, hanging or laid flat.',
        retryable: false,
      }
    case 'vision_service_error':
      return {
        title: 'Our image recognition hit a snag',
        message: 'This is usually temporary. Please try again in a moment.',
        retryable: true,
      }
    case 'network_error':
      return {
        title: "Can't reach EcoScan",
        message: 'Check your internet connection and try again.',
        retryable: true,
      }
    case 'validation_error':
      return {
        title: "Some details aren't valid",
        message: 'Check that every item has a type, then try again.',
        retryable: true,
      }
    default:
      return {
        title: 'Something went wrong',
        message: 'Please try again.',
        retryable: true,
      }
  }
}
