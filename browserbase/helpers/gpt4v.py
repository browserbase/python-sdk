from base64 import b64encode


def GPT4Image(img: bytes, detail: str):
    if not img:
        raise ValueError("Image was not provided")

    img_encoded = b64encode(img).decode()
    return {
        "type": "image_url",
        "image_url": {
            "url": "data:image/jpeg;base64," + img_encoded,
            "detail": detail,
        },
    }
