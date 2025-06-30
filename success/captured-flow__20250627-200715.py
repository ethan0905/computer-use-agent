# Prompt: [Captured Flow]
# Outcome: success

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Chrome actions
  Timestamp window: 2025-06-27 20:06:32 -> 20:06:46
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
property step1Pos : {1211, 49} -- Click position for the first action
property pageLoadDelay : 4 -- Delay for page load
property keyDelay : 0.1 -- Delay between keystrokes
property step2Pos : {768, 757} -- Click position for the second action
property step3Pos : {594, 510} -- Click position for the third action

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

-- 1. Click the specified position (1211, 49)
clickAt(step1Pos, 0.3)

-- 2. Type "meta.com" in the new tab
repeat with char in {"m", "e", "t", "a", ".", "c", "o", "m"}
    tell application "System Events" to keystroke char
    delay keyDelay
end repeat

-- 3. Press Return to navigate
tell application "System Events" to key code 36
delay keyDelay

-- 4. Click the specified position (768, 757)
clickAt(step2Pos, 0.3)

-- 5. Click the specified position (594, 510)
clickAt(step3Pos, 0.3)