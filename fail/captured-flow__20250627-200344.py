# Prompt: [Captured Flow]
# Outcome: fail

```applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-27 20:03:16 -> 20:03:25
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
property step1Pos : {1217, 49}  -- Click position for new tab button
property keyDelay : 0.1          -- Delay for key presses
property clickDelay : 0.3         -- Delay for mouse clicks
property finalClickPos : {587, 515} -- Final click position

------------------------------------------------------------
-- Helper: Click at specified coordinates
------------------------------------------------------------
on clickAt({x, y}, pause)
    global cli
    do shell script cli & "c:" & x & "," & y
    delay pause
end clickAt

------------------------------------------------------------
-- Main flow
------------------------------------------------------------
tell application "Google Chrome" to activate
delay 0.3

-- 1. Click the new-tab button
clickAt(step1Pos, clickDelay)

-- 2. Type "ycob" in the new tab
repeat with char in {"y", "c", "o", "b"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 3. Press backspace twice
repeat 2 times
    tell application "System Events" to key code 51 -- backspace
    delay keyDelay
end repeat

-- 4. Type "tor" and a comma
repeat with char in {"t", "o", "r", ","}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 5. Press backspace once
tell application "System Events" to key code 51 -- backspace
delay keyDelay

-- 6. Type "." and "com"
repeat with char in {".", "c", "o", "m"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 7. Type "/" and "start"
repeat with char in {"/", "s", "t", "a", "r", "t"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 8. Press Enter
tell application "System Events" to key code 36 -- Enter
delay keyDelay

-- 9. Final click inside the article
clickAt(finalClickPos, clickDelay)
```