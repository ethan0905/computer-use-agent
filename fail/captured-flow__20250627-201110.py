# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-27 20:09:54 -> 20:10:21
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
property step1Pos : {1217, 56}  -- Click position for the first action
property pageLoadDelay : 0.3      -- Delay for page loading
property keyDelay : 0.1            -- Delay between keystrokes

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
-- 1. Click the new-tab button
clickAt(step1Pos, pageLoadDelay)

-- 2. Type "youtube.com" in the address bar
tell application "System Events"
    keystroke "y"
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke "u"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke "u"
    delay keyDelay
    keystroke "b"
    delay keyDelay
    keystroke "e"
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
delay 4 -- wait for the page to load

-- 3. Click on the first video
clickAt({686, 153}, pageLoadDelay)

-- 4. Type "ethanx25" in the search bar
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
    keystroke "x"
    delay keyDelay
    keystroke "2"
    delay keyDelay
    keystroke "5"
    delay keyDelay
end tell

-- 5. Click on the second video
clickAt({370, 347}, pageLoadDelay)

-- 6. Scroll down
repeat 10 times
    tell application "System Events" to key code 126 -- up arrow
    delay 0.1
end repeat

-- 7. Click on the video
clickAt({233, 532}, pageLoadDelay)

-- 8. Click on another element
clickAt({611, 513}, pageLoadDelay)