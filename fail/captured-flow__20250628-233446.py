# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-28 23:33:39 -> 23:33:55
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
property step1Pos : {810, 50} -- Click position for the first action
property pageLoadDelay : 0.3 -- Delay for page load
property keyDelay : 0.1 -- Delay between key presses
property finalClickPos : {607, 509} -- Final click position

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

-- 1. Click the specified position
clickAt(step1Pos, pageLoadDelay)

-- 2. Type "chat.openai."
tell application "System Events"
    keystroke "c"
    delay keyDelay
    keystroke "h"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke "."
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke "p"
    delay keyDelay
    keystroke "e"
    delay keyDelay
    keystroke "n"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "i"
    delay keyDelay
    keystroke "."
    delay keyDelay
    keystroke "c"
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke "m"
    delay keyDelay
    keystroke "/"
    delay keyDelay
    keystroke "c"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke key code 51 -- backspace
    delay keyDelay
    keystroke "h"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke key code 36 -- Return
end tell

-- 3. Click the final position
clickAt(finalClickPos, pageLoadDelay)