# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-27 20:32:39 -> 20:33:31
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
property step1Pos : {1049, 56}  -- Click position for the first action
property pageLoadDelay : 0.3      -- Delay for page load
property keyDelay : 0.05           -- Delay for key presses
property clickDelay : 0.3          -- Delay for mouse clicks

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
-- 1. Click the first button in Google Chrome
clickAt(step1Pos, clickDelay)

-- 2. Type "gmail.com" in the address bar
tell application "System Events"
    keystroke "g"
    delay keyDelay
    keystroke "m"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "i"
    delay keyDelay
    keystroke "l"
    delay keyDelay
    keystroke "."
    delay keyDelay
    keystroke "c"
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke "m"
    delay keyDelay
    keystroke return
end tell
delay pageLoadDelay

-- 3. Click on the email in the inbox
clickAt({151, 216}, clickDelay)

-- 4. Type "ethan" in the email body
tell application "System Events"
    keystroke "e"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke "h"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "n"
    delay keyDelay
end tell

-- 5. Type "gmail.com" in the email body
tell application "System Events"
    keystroke "g"
    delay keyDelay
    keystroke "m"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "i"
    delay keyDelay
    keystroke "l"
    delay keyDelay
    keystroke "."
    delay keyDelay
    keystroke "c"
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke "m"
    delay keyDelay
end tell

-- 6. Click to send the email
clickAt({727, 473}, clickDelay)

-- 7. Type "Hello, this is a test email." in the email body
tell application "System Events"
    keystroke "H"
    delay keyDelay
    keystroke "e"
    delay keyDelay
    keystroke "l"
    delay keyDelay
    keystroke "l"
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke ","
    delay keyDelay
    keystroke " "
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke "h"
    delay keyDelay
    keystroke "i"
    delay keyDelay
    keystroke "s"
    delay keyDelay
    keystroke " "
    delay keyDelay
    keystroke "i"
    delay keyDelay
    keystroke "s"
    delay keyDelay
    keystroke " "
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke " "
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke "e"
    delay keyDelay
    keystroke "s"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke " "
    delay keyDelay
    keystroke "e"
    delay keyDelay
    keystroke "m"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "i"
    delay keyDelay
    keystroke "l"
    delay keyDelay
    keystroke "."
end tell

-- 8. Click to send the email
clickAt({713, 800}, clickDelay)