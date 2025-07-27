import requests
import keyboard
import time

# Replace with your ESP32 IP address
ESP32_IP = "http://192.168.1.80"  # CHANGE THIS

# Key to command mapping
key_map = {
    'w': '/forward',
    'a': '/left',
    's': '/backward',
    'd': '/right',
    'space': '/stop'
}

def send_command(path):
    url = f"{ESP32_IP}{path}"
    try:
        response = requests.get(url, timeout=0.5)
        print(f"Sent: {path} | Response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending {path}: {e}")

def main():
    print("Control the robot using W A S D and SPACE to stop.")
    print("Press ESC to exit.\n")

    while True:
        try:
            for key in key_map:
                if keyboard.is_pressed(key):
                    send_command(key_map[key])
                    time.sleep(0.2)  # Debounce delay
            if keyboard.is_pressed('esc'):
                print("Exiting...")
                break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
