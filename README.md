# Browserbase Python SDK

Example usage:

```
pip install browserbase
```

```py
from browserbase import Browserbase

# Loading a webpage
browserbase = Browserbase(os.environ["BROWSERBASE_KEY"])
result = browserbase.load("https://example.com")
```
