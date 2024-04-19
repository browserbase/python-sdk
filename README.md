# Browserbase Python SDK

[Browserbase](https://browserbase.com) is a serverless platform for running headless browsers, it offers advanced debugging, session recordings, stealth mode, integrated proxies and captcha solving.

## Installation and setup

- Get an API key from [browserbase.com](https://browserbase.com) and set it in environment variables (`BROWSERBASE_API_KEY`).
- Install the required dependencies:

```
pip install browserbase
```

## Usage

```py
from browserbase import Browserbase

# Init the SDK
browserbase = Browserbase(os.environ["BROWSERBASE_API_KEY"])

# Load a webpage
result = browserbase.load("https://example.com")

# Load multiple webpages (returns iterator)
result = browserbase.load(["https://example.com"])

# Text-only mode
result = browserbase.load("https://example.com", text_content=True)

# Screenshot (returns bytes)
result = browserbase.screenshot("https://example.com", full_page=True)
```
