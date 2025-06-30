# Prompt: [Captured Flow]
# Outcome: success

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-27 20:15:12 -> 20:15:38
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
property step1Pos : {1215, 55} -- Click position for the new tab
property keyDelay : 0.1 -- Delay for key presses
property clickDelay : 0.3 -- Delay for mouse clicks
property pageLoadDelay : 4 -- Delay for page load

------------------------------------------------------------
-- Helper: Click at specified coordinates
------------------------------------------------------------
on clickAt({x, y}, pause)
    global cli
    do shell script cli & "c:" & x & "," & y
    delay pause
end clickAt

------------------------------------------------------------
-- 1. Bring Chrome to the foreground
------------------------------------------------------------
tell application "Google Chrome" to activate
delay 0.3

------------------------------------------------------------
-- 2. Click the new-tab button
------------------------------------------------------------
clickAt(step1Pos, clickDelay)

------------------------------------------------------------
-- 3. Type "you.com" in the address bar
------------------------------------------------------------
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
delay pageLoadDelay

------------------------------------------------------------
-- 4. Click on the YouTube link
------------------------------------------------------------
clickAt({446, 148}, clickDelay)

------------------------------------------------------------
-- 5. Type "ethanx25" in the search bar
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
    keystroke return
end tell
delay pageLoadDelay

------------------------------------------------------------
-- 6. Click on the first video
------------------------------------------------------------
clickAt({354, 372}, clickDelay)

------------------------------------------------------------
-- 7. Click on the second video
------------------------------------------------------------
clickAt({245, 712}, clickDelay)

------------------------------------------------------------
-- 8. Click on the third video
------------------------------------------------------------
clickAt({446, 463}, clickDelay)

------------------------------------------------------------
-- 9. Click on the fourth video
------------------------------------------------------------
clickAt({599, 518}, clickDelay)