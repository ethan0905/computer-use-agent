# Prompt: [Captured Flow]
# Outcome: fail

applescript
(*
  ----------------------------------------------------------------------
  Replay of captured Google Chrome actions
  Timestamp window: 2025-06-27 20:08:54 -> 20:09:22
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
property step1Pos : {1040, 53}  -- Click position for Google Calendar
property pageLoadDelay : 0.3      -- Delay for page load
property keystrokeDelay : 0.1      -- Delay between keystrokes
property clickDelay : 0.3           -- Delay after clicks

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
-- 1. Click on the Google Calendar
clickAt(step1Pos, clickDelay)

-- 2. Type "youtube.com"
repeat with char in {"y", "o", "u", "t", "u", "b", "e", ".", "c", "o", "m"}
    tell application "System Events" to keystroke char
    delay keystrokeDelay
end repeat

-- 3. Press Return to navigate to the URL
tell application "System Events" to key code 36  -- Return key
delay pageLoadDelay

-- 4. Click on the YouTube video
clickAt({674, 154}, clickDelay)

-- 5. Type "ethanx25"
repeat with char in {"e", "t", "h", "a", "n", "x", "2", "5"}
    tell application "System Events" to keystroke char
    delay keystrokeDelay
end repeat

-- 6. Press Return to search
tell application "System Events" to key code 36  -- Return key
delay pageLoadDelay

-- 7. Click on the specific video
clickAt({539, 359}, clickDelay)

-- 8. Click on the like button (example coordinates)
clickAt({256, 553}, clickDelay)

-- 9. Click on the subscribe button (example coordinates)
clickAt({600, 512}, clickDelay)