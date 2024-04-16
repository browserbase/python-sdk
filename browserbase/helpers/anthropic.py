from base64 import b64encode


def Claude3Image(img: bytes):
    if not img:
        raise ValueError("Image was not provided")

    img_encoded = b64encode(img).decode()
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/png", "data": img_encoded},
    }
