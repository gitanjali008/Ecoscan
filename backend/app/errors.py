"""Custom errors and the handlers that turn them into JSON responses.

Services raise these instead of HTTP exceptions, so they stay free of HTTP
details. Every error reaches the client in the same shape:

    {"error": {"code": "image_too_large", "message": "..."}}
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class EcoScanError(Exception):
    """Base for every error the API reports on purpose."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "Something went wrong."

    def __init__(self, message: str | None = None) -> None:
        # Instances can give a more specific message; the class one is the default.
        if message is not None:
            self.message = message
        super().__init__(self.message)


class EmptyImageError(EcoScanError):
    status_code = 400
    code = "empty_image"
    message = "The uploaded image is empty."


class ImageTooLargeError(EcoScanError):
    status_code = 413
    code = "image_too_large"
    message = "The uploaded image is too large."


class InvalidImageError(EcoScanError):
    status_code = 415
    code = "invalid_image"
    message = "Upload a JPEG, PNG or WebP image."


class NoClothingDetectedError(EcoScanError):
    status_code = 422
    code = "no_clothing_detected"
    message = "No clothing items were found in the image."


class VisionServiceError(EcoScanError):
    status_code = 502
    code = "vision_service_error"
    message = "The image recognition service failed. Please try again."


def _error_body(code: str, message: str, **extra: object) -> dict:
    return {"error": {"code": code, "message": message, **extra}}


async def _handle_ecoscan_error(request: Request, exc: EcoScanError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=_error_body(exc.code, exc.message))


async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # jsonable_encoder: Pydantic error details can hold objects (e.g. a ValueError) that plain JSON cannot.
    return JSONResponse(
        status_code=422,
        content=_error_body(
            "validation_error",
            "The request data is invalid.",
            details=jsonable_encoder(exc.errors()),
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EcoScanError, _handle_ecoscan_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
