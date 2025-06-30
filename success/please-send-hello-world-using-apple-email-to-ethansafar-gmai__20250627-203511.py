# Prompt: please send hello world using apple email to ethansafar@gmail.com
# Outcome: success

import subprocess
import time

def check_app_running(app_name):
    try:
        output = subprocess.check_output(["pgrep", app_name])
        return True if output else False
    except subprocess.CalledProcessError:
        return False

def open_mail_app():
    if not check_app_running("Mail"):
        subprocess.Popen(["open", "-a", "Mail"])
        time.sleep(5)  # Wait for the app to launch

def send_email(to_address, subject, body):
    open_mail_app()
    
    try:
        # Use AppleScript to send the email
        apple_script = f'''
        tell application "Mail"
            set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
            tell newMessage
                make new to recipient at end of to recipients with properties {{address:"{to_address}"}}
                send
            end tell
        end tell
        '''
        subprocess.run(["osascript", "-e", apple_script])
        print(f"Email sent to {to_address}.")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

if __name__ == "__main__":
    send_email("ethansafar@gmail.com", "Hello World", "Hello, World!")