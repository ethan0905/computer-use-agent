# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Chrome actions
  Timestamp window: 2025-06-29 10:15:55 -> 10:16:32
  Requirements  :  - Google Chrome
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
property step1Pos : {575, 50}  -- Click position for the first action
property keyDelay : 0.1          -- Delay for key presses
property clickDelay : 0.3         -- Delay for mouse clicks
property scrollDelay : 0.05       -- Delay for scroll actions

------------------------------------------------------------
-- Main flow
------------------------------------------------------------
-- 1. Bring Chrome to the foreground
tell application "Google Chrome" to activate
delay 0.3

-- 2. Click at the specified coordinates
clickAt(step1Pos, clickDelay)

-- 3. Type "yc" into the active field
repeat with char in {"y", "c"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 4. Type "ombina" into the active field
repeat with char in {"o", "m", "b", "i", "n", "a"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 5. Type "t" into the active field
tell application "System Events" to keystroke "t"
delay keyDelay

-- 6. Type "or" into the active field
repeat with char in {"o", "r"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 7. Type ".com" into the active field
repeat with char in {".", "c", "o", "m"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 8. Press Return to submit
tell application "System Events" to key code 36
delay keyDelay

-- 9. Click on the Y Combinator link
clickAt({292, 160}, clickDelay)

-- 10. Scroll down the page
repeat 10 times
    tell application "System Events" to key code 126 -- up arrow
    delay scrollDelay
end repeat

-- 11. Click on a specific item in the Y Combinator page
clickAt({174, 388}, clickDelay)

-- 12. Scroll down the page
repeat 10 times
    tell application "System Events" to key code 126 -- up arrow
    delay scrollDelay
end repeat

-- 13. Click on another item in the Y Combinator page
clickAt({192, 732}, clickDelay)

-- 14. Scroll down the page
repeat 10 times
    tell application "System Events" to key code 126 -- up arrow
    delay scrollDelay
end repeat

-- 15. Click on a specific link
clickAt({619, 507}, clickDelay)

------------------------------------------------------------
-- Helper function for clicking
------------------------------------------------------------
on clickAt({x, y}, pause)
    do shell script cli & "c:" & x & "," & y
    delay pause
end clickAt