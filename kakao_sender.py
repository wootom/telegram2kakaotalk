import subprocess
import time
import sys

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 5  # seconds

def send_to_kakao(room_name, message, retry_count=0):
    """
    VAAX 카카오톡 채팅방에 메시지를 전송합니다.
    전제조건: VAAX 창이 항상 열려 있어야 합니다.
    실패 시 최대 3회까지 재시도합니다.
    """
    if not room_name or not message:
        return False

    # 1. 클립보드에 메시지 복사 (한글 깨짐 방지)
    try:
        subprocess.run(['pbcopy'], input=message.encode('utf-8'), check=True, timeout=5)
    except Exception as e:
        print(f"클립보드 복사 실패: {e}")
        return False

    scpt = f"""
    tell application "KakaoTalk" to activate
    delay 1

    tell application "System Events"
        tell application process "KakaoTalk"
            set frontmost to true
            delay 0.5
            
            -- Find VAAX window
            set vaaxWin to missing value
            repeat with win in windows
                if name of win is "{room_name}" then
                    set vaaxWin to win
                    exit repeat
                end if
            end repeat
            
            if vaaxWin is missing value then
                return "ERROR: {room_name} window not found."
            end if
            
            -- Raise window
            perform action "AXRaise" of vaaxWin
            delay 0.5
            
            -- Get position and size
            set {{vX, vY}} to position of vaaxWin
            set {{vW, vH}} to size of vaaxWin
            
            -- Click input area (center, 80px from bottom)
            click at {{vX + (vW / 2), vY + vH - 80}}
            delay 0.5
            
            -- Clear any existing text
            keystroke "a" using {{command down}}
            delay 0.1
            key code 51 -- Delete
            delay 0.2
            
            -- Paste from clipboard (Cmd+V) using key code
            key code 9 using {{command down}}
            delay 0.5
            
            -- Send: Tab + Enter
            key code 48 -- Tab
            delay 0.2
            key code 36 -- Enter
            delay 0.3
            
            return "SUCCESS"
        end tell
    end tell
    """
    
    try:
        cmd = ['osascript', '-e', scpt]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if "SUCCESS" in output:
            print(f"Message sent successfully!")
            return True
        else:
            print(f"Result: {output}")
            return False
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or str(e)
        print(f"Error: {error_msg}")
        
        # Check for accessibility permission error (-25211) and retry
        if "-25211" in error_msg or "보조 접근" in error_msg:
            if retry_count < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** retry_count)  # Exponential backoff
                print(f"⚠️ Accessibility permission issue. Retrying in {delay} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(delay)
                return send_to_kakao(room_name, message, retry_count + 1)
            else:
                print(f"❌ Max retries ({MAX_RETRIES}) reached. Message failed to send.")
        
        return False

if __name__ == "__main__":
    if len(sys.argv) == 3:
        send_to_kakao(sys.argv[1], sys.argv[2])
    else:
        # Default test
        send_to_kakao("VAAX", "테스트 메시지입니다!")
