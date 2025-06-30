# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured actions
  Timestamp window: 2025-06-27 14:34:43 -> 14:34:55
  Requirements  :  - Application Name
                   - "cliclick" utility   ->  brew install cliclick
  ----------------------------------------------------------------------
*)

------------------------------------------------------------
-- Helper: find the first "cliclick" available on $PATH
------------------------------------------------------------
on cliPath()
    try
        return (do shell script "command -v cliclick") & " "
    on error
        display dialog "The helper utility 'cliclick' isn't installed or isn't on your PATH.\n\nInstall it with Homebrew:\n    brew install cliclick" buttons {"OK"} default button 1
        error number -128
    end try
end cliPath

property cli : cliPath()  -- prepend to every "cliclick" shell command

------------------------------------------------------------
-- User-tunable block
------------------------------------------------------------
property step1Pos : {1216, 52}  -- Coordinates for new-tab button
property step2URL : "https://www.perplexity.ai"  -- URL to open
property step3Pos : {43, 391}  -- Coordinates for left-hand "Perplexity" item
property step4Pos : {684, 519}  -- Coordinates for "Discover" card
property scrollCount : 14  -- Number of scrolls
property scrollDelay : 0.05  -- Delay between scrolls
property step5Pos : {744, 471}  -- Coordinates for DeepSeek headline
property step6Pos : {641, 508}  -- Coordinates for final click
property pageLoadDelay : 4  -- Delay for page load
property clickDelay : 0.3  -- Delay after clicks

------------------------------------------------------------
-- Helper function to click at specified coordinates
------------------------------------------------------------
on clickAt({x, y}, pause)
    global cli
    do shell script cli & "c:" & x & "," & y
    delay pause
end clickAt

------------------------------------------------------------
-- 1. Bring Application to the foreground
------------------------------------------------------------
tell application "Application Name" to activate
delay clickDelay

------------------------------------------------------------
-- 2. Click the new-tab button
------------------------------------------------------------
clickAt(step1Pos, clickDelay)

------------------------------------------------------------
-- 3. Load URL in that tab
------------------------------------------------------------
tell application "Application Name"
    open location step2URL
end tell
delay pageLoadDelay -- let the page finish loading

------------------------------------------------------------
-- 4. Click the left-hand "Perplexity" item
------------------------------------------------------------
clickAt(step3Pos, clickDelay)

------------------------------------------------------------
-- 5. Click the "Discover" card
------------------------------------------------------------
clickAt(step4Pos, clickDelay)

------------------------------------------------------------
-- 6. Recreate the scrolls
------------------------------------------------------------
repeat scrollCount times
    tell application "System Events" to key code 126 -- up arrow
    delay scrollDelay
end repeat
delay 0.5

------------------------------------------------------------
-- 7. Click the DeepSeek headline
------------------------------------------------------------
clickAt(step5Pos, clickDelay)

------------------------------------------------------------
-- 8. Final click inside the article
------------------------------------------------------------
clickAt(step6Pos, clickDelay)