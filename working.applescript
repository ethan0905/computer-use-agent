------------------------------------------------------------------------------
--  Perplexity Quick-Flow
--  • Install cliclick →  brew install cliclick
--  • Tick the app that runs this script in:
--      System Settings ▸ Privacy & Security ▸ Accessibility  and  Input Monitoring
--  • Replace the coordinate pairs below with the ones that match your screen
------------------------------------------------------------------------------

use scripting additions

-------------------------------------------------------------------------------
--  USER-TUNABLE SETTINGS
-------------------------------------------------------------------------------
property discoverPos : {41, 396}   -- ← coords of the “Discover” button
property articlePos  : {423, 492}  -- ← coords of the “Article” choice
property pageLoadDelay : 2.0       -- seconds to let the page finish rendering
-------------------------------------------------------------------------------

-- Will hold the absolute path to cliclick
property cli : missing value

-- 1 ▸ Locate cliclick --------------------------------------------------------
set possiblePaths to {"/opt/homebrew/bin/cliclick", "/usr/local/bin/cliclick"}
repeat with p in possiblePaths
    if (do shell script "test -x " & quoted form of p & " && echo 1 || echo 0") is "1" then
        set cli to p
        exit repeat
    end if
end repeat

if cli is missing value then
    display dialog ¬
        "Couldn’t find “cliclick”. Install it with Homebrew (“brew install cliclick”) " & ¬
        "or edit this script to point to its location." with icon stop buttons {"Quit"} default button 1
    return
end if

-- 2 ▸ Helper handler ---------------------------------------------------------
on clickAt(pt as list, pause as real)
    global cli
    do shell script cli & " c:" & (item 1 of pt) & "," & (item 2 of pt)
    delay pause
end clickAt

-- 3 ▸ The automation sequence -----------------------------------------------
do shell script "open https://www.perplexity.ai"
delay pageLoadDelay

clickAt(discoverPos, 0.25)
clickAt(articlePos, 0.25)

