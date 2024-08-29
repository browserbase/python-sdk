# %%import json
from IPython.display import HTML, display

# Assuming 'data' contains your rrweb events
# If not, replace 'data' with your actual events data

SESSION_ID = "SESSION_ID"

html_content = f"""
<div id="BB_LIVE_SESSION_{SESSION_ID}"></div>
<script src="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/rrweb-player@latest/dist/index.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/rrweb-player@latest/dist/style.css"/>

<script>
(function() {{
    var events = {json.dumps(data)};
    
    function initPlayer() {{
        if (typeof rrwebPlayer === 'undefined') {{
            console.log('rrweb player not loaded yet, retrying...');
            setTimeout(initPlayer, 100);
            return;
        }}
        
        new rrwebPlayer({{
            target: document.getElementById('BB_LIVE_SESSION_{SESSION_ID}'),
            props: {{
                events: events,
                width: 800,
                height: 600,
                autoPlay: true
            }}
        }});
    }}
    
    if (document.readyState === 'complete') {{
        initPlayer();
    }} else {{
        window.addEventListener('load', initPlayer);
    }}
}})();
</script>
"""

display(HTML(html_content))
# %%
