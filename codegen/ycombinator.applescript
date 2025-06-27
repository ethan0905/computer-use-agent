(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-27 19:57:16 -> 19:57:23
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
property step1Pos : {1211, 54} -- Click position for the new tab button
property pageLoadDelay : 4 -- Delay for page load
property keyDelay : 0.1 -- Delay between key presses
property finalClickPos : {604, 514} -- Final click position

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
clickAt(step1Pos, 0.3)

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

-- 17. Press Enter
tell application "System Events"
    key code 36 -- Enter key
    delay keyDelay
end tell

-- 18. Click the final position
clickAt(finalClickPos, 0.3)
