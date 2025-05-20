import cv2
import requests
import datetime
import os
import time

# ---- CONFIG ----
THINGSPEAK_CHANNEL_ID = "2824969"
THINGSPEAK_READ_API_KEY = "VEWYVXONJ64CDSSH"
NUM_RESULTS = 1
SAVE_DIR = r"D:\test\capture image"
GAS_THRESHOLD = 400
CHECK_INTERVAL = 10  # seconds

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_sensor_data():
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {
        "api_key": THINGSPEAK_READ_API_KEY,
        "results": NUM_RESULTS
    }
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if "feeds" not in data or not data["feeds"]:
                print("WARNING: No data available from ThingSpeak.")
                return None

            latest_feed = data["feeds"][-1]
            temperature = float(latest_feed["field1"])
            humidity = float(latest_feed["field2"])
            gas = float(latest_feed["field3"])
            return temperature, humidity, gas

        except Exception as e:
            print(f"ERROR: Failed to fetch data - {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(5)  # Wait before retrying
    return None  # Return None after retries fail

def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fruit_{timestamp}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(filepath, frame)
        print(f"Image saved at: {filepath}")
        # Optional: Display the image for 3 seconds
        cv2.imshow("Captured Image", frame)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()
    else:
        print("ERROR: Failed to capture image.")

def main():
    print("=== Starting automatic sensor monitor ===")
    while True:
        sensor_data = fetch_sensor_data()
        if sensor_data:
            temperature, humidity, gas = sensor_data
            print(f"Temperature: {temperature} °C | Humidity: {humidity} % | Gas: {gas} PPM")

            if gas > GAS_THRESHOLD:
                print(f"Gas level {gas} is above threshold {GAS_THRESHOLD}. Capturing image...")
                capture_image()
            else:
                print(f"Gas level {gas} is below threshold. Skipping image capture.")

        else:
            print("Skipping this cycle due to data fetch error.")

        print(f"Waiting {CHECK_INTERVAL} seconds for next check...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
