(*
  ----------------------------------------------------------------------
  Replay of captured Chrome actions
  Timestamp window: 2025-06-27 14:34:43 → 14:34:55
  Requirements  :  • Google Chrome
                   • “cliclick” utility   →  brew install cliclick
  ----------------------------------------------------------------------
*)

------------------------------------------------------------
-- Helper: find the first ‘cliclick’ available on $PATH
------------------------------------------------------------
on cliPath()
    try
        return (do shell script "command -v cliclick") & " "
    on error
        display dialog ¬
            "The helper utility “cliclick” isn’t installed or isn’t on your PATH.\n\n" & ¬
            "Install it with Homebrew:\n    brew install cliclick" buttons {"OK"} default button 1
        error number -128
    end try
end cliPath

property c : cliPath()  -- prepend to every ‘cliclick’ shell command

------------------------------------------------------------
-- 1. Bring Chrome to the foreground
------------------------------------------------------------
tell application "Google Chrome" to activate
delay 0.3

------------------------------------------------------------
-- 2. Click the new-tab button  (coords 1216 × 52)
------------------------------------------------------------
do shell script c & "c:1216,52"
delay 0.3

------------------------------------------------------------
-- 3. Load Perplexity in that tab
------------------------------------------------------------
tell application "Google Chrome"
    open location "https://www.perplexity.ai"
end tell
delay 4 -- let the page finish loading

------------------------------------------------------------
-- 4. Click the left-hand “Perplexity” item  (43 × 391)
------------------------------------------------------------
do shell script c & "c:43,391"
delay 1

------------------------------------------------------------
-- 5. Click the “Discover” card  (684 × 519)
------------------------------------------------------------
do shell script c & "c:684,519"
delay 1.5

------------------------------------------------------------
-- 6. Recreate the nine small upward scrolls in the log
------------------------------------------------------------
repeat 14 times
    tell application "System Events" to key code 126 -- ↑ arrow
    delay 0.05
end repeat
delay 0.5

------------------------------------------------------------
-- 7. Click the DeepSeek headline  (744 × 471)
------------------------------------------------------------
do shell script c & "c:744,471"
delay 2

------------------------------------------------------------
-- 8. Final click inside the article  (641 × 508)
------------------------------------------------------------
do shell script c & "c:641,508"

