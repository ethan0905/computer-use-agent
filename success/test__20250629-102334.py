# Prompt: test
# Outcome: success

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-29 10:20:49 -> 10:21:19
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
property step1Pos : {802, 48}  -- Click position for the first action
property keyDelay : 0.1         -- Delay for key presses
property clickDelay : 0.3        -- Delay for mouse clicks
property scrollDelay : 0.05      -- Delay for scrolling actions

------------------------------------------------------------
-- Helper: Click at specified coordinates
------------------------------------------------------------
on clickAt({x, y}, pause)
    global cli
    do shell script cli & " c:" & x & "," & y
    delay pause
end clickAt

------------------------------------------------------------
-- Main flow
------------------------------------------------------------
tell application "Google Chrome" to activate
delay 0.3

-- 1. Click on the specified position
clickAt(step1Pos, clickDelay)

-- 2. Type "y"
tell application "System Events"
    keystroke "y"
    delay keyDelay
end tell

-- 3. Type "c"
tell application "System Events"
    keystroke "c"
    delay keyDelay
end tell

-- 4. Type "o"
tell application "System Events"
    keystroke "o"
    delay keyDelay
end tell

-- 5. Type "m"
tell application "System Events"
    keystroke "m"
    delay keyDelay
end tell

-- 6. Type "b"
tell application "System Events"
    keystroke "b"
    delay keyDelay
end tell

-- 7. Type "i"
tell application "System Events"
    keystroke "i"
    delay keyDelay
end tell

-- 8. Type "n"
tell application "System Events"
    keystroke "n"
    delay keyDelay
end tell

-- 9. Type "a"
tell application "System Events"
    keystroke "a"
    delay keyDelay
end tell

-- 10. Type "t"
tell application "System Events"
    keystroke "t"
    delay keyDelay
end tell

-- 11. Type "o"
tell application "System Events"
    keystroke "o"
    delay keyDelay
end tell

-- 12. Type "r"
tell application "System Events"
    keystroke "r"
    delay keyDelay
end tell

-- 13. Type "."
tell application "System Events"
    keystroke "."
    delay keyDelay
end tell

-- 14. Type "c"
tell application "System Events"
    keystroke "c"
    delay keyDelay
end tell

-- 15. Type "o"
tell application "System Events"
    keystroke "o"
    delay keyDelay
end tell

-- 16. Type "m"
tell application "System Events"
    keystroke "m"
    delay keyDelay
end tell

-- 17. Press Return
tell application "System Events"
    key code 36 -- Return key
end tell
delay clickDelay

-- 18. Click on the specified position for Y Combinator
clickAt({309, 164}, clickDelay)

-- 19. Scroll down multiple times
repeat 10 times
    tell application "System Events" to key code 126 -- up arrow
    delay scrollDelay
end repeat

-- 20. Click on the specified position for the next action
clickAt({173, 409}, clickDelay)

-- 21. Click on the specified position for the next action
clickAt({191, 659}, clickDelay)

-- 22. Scroll down multiple times
repeat 10 times
    tell application "System Events" to key code 125 -- down arrow
    delay scrollDelay
end repeat

-- 23. Click on the specified position for the final action
clickAt({595, 517}, clickDelay)