import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.errors import (
    EcoScanError,
    EmptyImageError,
    ImageTooLargeError,
    InvalidImageError,
    NoClothingDetectedError,
    VisionServiceError,
    register_error_handlers,
)
from app.main import create_app

ERRORS = {
    "empty": EmptyImageError,
    "too-large": ImageTooLargeError,
    "invalid": InvalidImageError,
    "no-clothing": NoClothingDetectedError,
    "vision": VisionServiceError,
}


class Body(BaseModel):
    count: int


def make_test_app() -> FastAPI:
    test_app = FastAPI()
    register_error_handlers(test_app)

    @test_app.get("/raise/{name}")
    def raise_error(name: str):
        raise ERRORS[name]()

    @test_app.get("/custom-message")
    def custom_message():
        raise ImageTooLargeError("Image is 7.2 MB, the limit is 5 MB.")

    @test_app.post("/body")
    def needs_body(body: Body):
        return body

    return test_app


client = TestClient(make_test_app())


@pytest.mark.parametrize(
    "name, status, code",
    [
        ("empty", 400, "empty_image"),
        ("too-large", 413, "image_too_large"),
        ("invalid", 415, "invalid_image"),
        ("no-clothing", 422, "no_clothing_detected"),
        ("vision", 502, "vision_service_error"),
    ],
)
def test_each_error_returns_its_status_and_json_shape(name, status, code):
    response = client.get(f"/raise/{name}")

    assert response.status_code == status
    assert response.json() == {"error": {"code": code, "message": ERRORS[name].message}}


def test_custom_message_replaces_the_default():
    response = client.get("/custom-message")

    assert response.json()["error"]["message"] == "Image is 7.2 MB, the limit is 5 MB."


def test_every_error_is_an_ecoscan_error():
    assert all(issubclass(error, EcoScanError) for error in ERRORS.values())


def test_validation_error_uses_the_same_shape():
    response = client.post("/body", json={"count": "not a number"})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["message"]
    assert error["details"][0]["loc"] == ["body", "count"]


def test_missing_body_is_a_validation_error():
    response = client.post("/body")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_real_app_registers_the_handlers():
    handlers = create_app().exception_handlers

    assert EcoScanError in handlers
    assert RequestValidationError in handlers
