# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-29 15:50:48 -> 15:51:05
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
property step1Pos : {1052, 45}  -- Click position for the first action
property step2Delay : 0.3         -- Delay after the first click
property keyDelay : 0.1           -- Delay between keystrokes
property step3Pos : {696, 154}    -- Click position for YouTube
property step4Delay : 0.5         -- Delay after YouTube click
property step5Pos : {404, 326}    -- Click position for ethanx25 YouTube
property scrollDelay : 0.1         -- Delay for scrolling actions
property finalClickPos : {615, 516} -- Final click position

------------------------------------------------------------
-- Helper: click at specified coordinates
------------------------------------------------------------
on clickAt({x, y}, pause)
    global cli
    do shell script cli & "c:" & x & "," & y
    delay pause
end clickAt

------------------------------------------------------------
-- Main flow
------------------------------------------------------------

------------------------------------------------------------
-- 1. Click the Y Combinator window (coords 1052 x 45)
------------------------------------------------------------
clickAt(step1Pos, step2Delay)

------------------------------------------------------------
-- 2. Type "you" in the New Tab
------------------------------------------------------------
tell application "System Events"
    keystroke "y"
    delay keyDelay
    keystroke "o"
    delay keyDelay
    keystroke "u"
    delay keyDelay
end tell

------------------------------------------------------------
-- 3. Press Enter to search
------------------------------------------------------------
tell application "System Events"
    key code 36 -- Return key
end tell
delay step4Delay

------------------------------------------------------------
-- 4. Click the YouTube link (coords 696 x 154)
------------------------------------------------------------
clickAt(step3Pos, step2Delay)

------------------------------------------------------------
-- 5. Type "ethanx25" in the YouTube search
------------------------------------------------------------
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

------------------------------------------------------------
-- 6. Press Enter to search
------------------------------------------------------------
tell application "System Events"
    key code 36 -- Return key
end tell
delay step4Delay

------------------------------------------------------------
-- 7. Click the ethanx25 video (coords 404 x 326)
------------------------------------------------------------
clickAt(step5Pos, step2Delay)

------------------------------------------------------------
-- 8. Scroll down in the video
------------------------------------------------------------
repeat 10 times
    tell application "System Events" to key code 126 -- up arrow
    delay scrollDelay
end repeat

------------------------------------------------------------
-- 9. Final click on the video (coords 615 x 516)
------------------------------------------------------------
clickAt(finalClickPos, step2Delay)