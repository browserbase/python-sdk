# Browserbase Python SDK

Example usage:

```
pip install browserbase
```

```py
from browserbase import Browserbase

# Init the SDK
browserbase = Browserbase(os.environ["BROWSERBASE_KEY"])

# Load a webpage
result = browserbase.load("https://example.com")

# Load multiple webpages (returns iterator)
result = browserbase.load(["https://example.com"])

# Text-only mode
result = browserbase.load("https://example.com", text_content=True)

# Screenshot (returns bytes)
result = browserbase.screenshot("https://example.com", full_page=True)
```
