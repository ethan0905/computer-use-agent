(*  Replay of interaction log: 2025-06-27 14:34:43 → 14:34:55
    Prerequisites:
    • Google Chrome installed and running.
    • “cliclick” installed (brew install cliclick).

    This script reproduces:
      – Opening a new tab
      – Navigating to Perplexity.ai
      – Interface clicks
      – Scrolling through content
      – Selecting an article
*)

on cliPath()
    try
        return (do shell script "command -v cliclick") & " "
    on error
        display dialog "Install cliclick:  brew install cliclick" buttons {"OK"} default button 1
        error number -128
    end try
end cliPath
property c : cliPath()

-- 1. Click Chrome’s “New Tab” (+) button
do shell script c & "c:1217,53"
delay 0.5

-- 2. Load Perplexity.ai directly (no typed URL)
tell application "Google Chrome"
    activate
    open location "https://perplexity.ai"
end tell
delay 1.5

-- 3. Click side navigation item
do shell script c & "c:44,391"
delay 0.5

-- 4. Click the “Discover” card
do shell script c & "c:684,519"
delay 0.5

-- 5. Scroll down the article (12 downward steps)
repeat 12 times
    tell application "System Events" to key code 125 -- Down arrow
    delay 0.1
end repeat
delay 0.5

-- 6. Open the highlighted article link
do shell script c & "c:744,472"
delay 0.5

-- 7. Click inside the article body
do shell script c & "c:641,508"
delay 0.5

