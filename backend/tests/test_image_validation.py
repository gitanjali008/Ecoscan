import pytest

from app.errors import EmptyImageError, ImageTooLargeError, InvalidImageError
from app.services.image_validation import detect_image_type, validate_image

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 20
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 20
TEXT = b"just some text, renamed to photo.jpg"

LIMIT = 1024


@pytest.mark.parametrize(
    "data, expected",
    [
        (JPEG, "image/jpeg"),
        (PNG, "image/png"),
        (WEBP, "image/webp"),
        (TEXT, None),
        (b"GIF89a" + b"\x00" * 10, None),       # real image, but not an allowed type
        (b"RIFF\x24\x00\x00\x00WAVE", None),    # RIFF, but audio
        (b"\xff\xd8", None),                    # too short to be a JPEG
        (b"", None),
    ],
)
def test_detect_image_type(data, expected):
    assert detect_image_type(data) == expected


@pytest.mark.parametrize(
    "data, content_type",
    [(JPEG, "image/jpeg"), (PNG, "image/png"), (WEBP, "image/webp")],
)
def test_valid_images_pass_and_return_their_type(data, content_type):
    assert validate_image(data, content_type, LIMIT) == content_type


@pytest.mark.parametrize("content_type", ["image/jpg", "IMAGE/JPEG", "image/jpeg; charset=binary"])
def test_common_content_type_variants_are_accepted(content_type):
    assert validate_image(JPEG, content_type, LIMIT) == "image/jpeg"


@pytest.mark.parametrize("content_type", ["text/plain", "image/gif", "application/pdf", "", None])
def test_unsupported_content_type_is_rejected(content_type):
    with pytest.raises(InvalidImageError):
        validate_image(JPEG, content_type, LIMIT)


def test_empty_file_is_rejected():
    with pytest.raises(EmptyImageError):
        validate_image(b"", "image/jpeg", LIMIT)


def test_file_over_the_limit_is_rejected_with_the_limit_in_mb():
    one_mb = 1024 * 1024

    with pytest.raises(ImageTooLargeError, match="limit is 1 MB"):
        validate_image(JPEG + b"\x00" * one_mb, "image/jpeg", one_mb)


def test_file_exactly_at_the_limit_is_allowed():
    data = JPEG + b"\x00" * (LIMIT - len(JPEG))

    assert validate_image(data, "image/jpeg", LIMIT) == "image/jpeg"


def test_renamed_text_file_is_rejected():
    with pytest.raises(InvalidImageError, match="not a valid"):
        validate_image(TEXT, "image/jpeg", LIMIT)


def test_real_type_wins_over_the_declared_one():
    # A PNG sent as image/jpeg is still a fine image; the vision provider gets the true type.
    assert validate_image(PNG, "image/jpeg", LIMIT) == "image/png"


def test_checks_run_in_order_type_then_empty():
    with pytest.raises(InvalidImageError):
        validate_image(b"", "text/plain", LIMIT)
