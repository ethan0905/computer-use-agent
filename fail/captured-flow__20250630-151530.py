# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Chrome actions
  Timestamp window: 2025-06-30 15:14:11 -> 15:14:35
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
property step1Pos : {568, 53} -- Click position for the first action
property step2Delay : 0.3
property keyDelay : 0.1
property step3Pos : {989, 153} -- Click position for the second action
property step4Pos : {565, 342} -- Click position for the third action
property step5Pos : {570, 315} -- Click position for the fourth action
property step6Delay : 0.1
property step7Pos : {544, 404} -- Click position for the fifth action
property step8Pos : {610, 630} -- Click position for the sixth action

------------------------------------------------------------
-- Helper: click at specified coordinates with a pause
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
-- 1. Bring Chrome to the foreground
------------------------------------------------------------
tell application "Google Chrome" to activate
delay step2Delay

------------------------------------------------------------
-- 2. Click the initial position (568, 53)
------------------------------------------------------------
clickAt(step1Pos, step2Delay)

------------------------------------------------------------
-- 3. Type "chatpen" with pauses
------------------------------------------------------------
tell application "System Events"
    keystroke "c"
    delay keyDelay
    keystroke "h"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    keystroke ","
    delay keyDelay
    key code 51 -- backspace
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
    keystroke "h"
    delay keyDelay
    keystroke "a"
    delay keyDelay
    keystroke "t"
    delay keyDelay
    key code 36 -- Return
end tell

------------------------------------------------------------
-- 4. Click the second position (989, 153)
------------------------------------------------------------
clickAt(step3Pos, step2Delay)

------------------------------------------------------------
-- 5. Click the third position (565, 342)
------------------------------------------------------------
clickAt(step4Pos, step2Delay)

------------------------------------------------------------
-- 6. Click the fourth position (570, 315)
------------------------------------------------------------
clickAt(step5Pos, step2Delay)

------------------------------------------------------------
-- 7. Type "ethan" with pauses
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
end tell

------------------------------------------------------------
-- 8. Click the fifth position (544, 404)
------------------------------------------------------------
clickAt(step7Pos, step2Delay)

------------------------------------------------------------
-- 9. Click the sixth position (610, 630)
------------------------------------------------------------
clickAt(step8Pos, step2Delay)