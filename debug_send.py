import subprocess
import time
import os

def debug_send():
    msg = "DEBUG_TEST_MESSAGE"
    scpt = """
    on run {target}
        tell application "KakaoTalk" to activate
        delay 2.0
        tell application "System Events"
            tell process "KakaoTalk"
                set frontmost to true
                delay 1.0
                set targetWindow to missing value
                repeat with win in windows
                    if name of win contains target then
                        set targetWindow to win
                        exit repeat
                    end if
                end repeat
                
                if targetWindow is not missing value then
                    perform action "AXRaise" of targetWindow
                    delay 1.0
                    -- Option 1: Just keystroke directly
                    keystroke "THIS_IS_A_Direct_Type_Test"
                    delay 1.0
                    -- Option 2: Clipboard Paste
                    set the clipboard to "THIS_IS_A_Clipboard_Paste_Test"
                    keystroke "v" using {command down}
                    delay 1.0
                    key code 36
                else
                    return "Window Not Found"
                end if
                return "Completed"
            end tell
        end tell
    end run
    """
    cmd = ['osascript', '-e', scpt, "VAAX"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"OUT: {r.stdout}")
    print(f"ERR: {r.stderr}")
    
    # Take screenshot after 5 seconds to see result
    time.sleep(2)
    subprocess.run(['screencapture', '/Users/woojanghoon/Documents/Code/vaax-telegram/debug_screen.png'])

if __name__ == "__main__":
    debug_send()
