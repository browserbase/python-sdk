from base64 import b64encode
from enum import Enum


class GPT4VImageDetail(Enum):
    low = "low"
    high = "high"
    auto = "auto"


def GPT4VImage(img: bytes, detail: GPT4VImageDetail = GPT4VImageDetail.auto):
    if not img:
        raise ValueError("Image was not provided")

    img_encoded = b64encode(img).decode()
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{img_encoded}",
            "detail": detail.value,
        },
    }
