from pathlib import Path

from bot import classify, extract_pinterest_url


def test_accepts_pinterest_urls():
    assert extract_pinterest_url("Look https://www.pinterest.com/pin/12345/ now") == "https://www.pinterest.com/pin/12345/"
    assert extract_pinterest_url("https://pin.it/AbCd123") == "https://pin.it/AbCd123"
    assert extract_pinterest_url("https://uk.pinterest.com/pin/123/") is not None


def test_rejects_lookalike_and_unrelated_hosts():
    assert extract_pinterest_url("https://pinterest.com.evil.example/pin/1") is None
    assert extract_pinterest_url("https://example.com/") is None
    assert extract_pinterest_url("hello") is None


def test_classifies_media():
    assert classify(Path("photo.JPG")) == "photo"
    assert classify(Path("clip.mp4")) == "video"
    assert classify(Path("metadata.json")) == "document"
