import time
import board
import busio
import adafruit_tcs34725

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create a sensor object
sensor = adafruit_tcs34725.TCS34725(i2c)

# Set integration time and gain
sensor.integration_time = 50
sensor.gain = 16

# Enable LED
sensor.led = False

# Function to normalize RGB values
def normalize_color(r, g, b):
    # Find the max of r, g, b to normalize the values
    max_value = max(r, g, b)
    
    # Avoid division by zero
    if max_value == 0:
        return 0, 0, 0

    # Normalize RGB to 0-255 range
    normalized_r = int((r / max_value) * 255)
    normalized_g = int((g / max_value) * 255)
    normalized_b = int((b / max_value) * 255)

    return normalized_r, normalized_g, normalized_b

# Function to detect color based on normalized RGB values
def detect_color(r, g, b):
    if r > 200 and g < 100 and b < 100:
        return "Red"
    elif g > 200 and r < 100 and b < 100:
        return "Green"
    elif b > 200 and r < 100 and g < 100:
        return "Blue"
    elif r > 200 and g > 200 and b < 100:
        return "Yellow"
    elif r > 150 and g > 100 and b > 150:
        return "Purple"
    elif r < 50 and g < 50 and b < 50:
        return "Black"
    elif r > 200 and g > 200 and b > 200:
        return "White"
    else:
        return "Unknown color"

# Main function to read color and detect it
def read_and_detect_color():
    # Get raw RGB and clear values
    r, g, b, c = sensor.color_raw
    
    # Normalize the RGB values
    norm_r, norm_g, norm_b = normalize_color(r, g, b)
    
    # Detect color
    detected_color = detect_color(norm_r, norm_g, norm_b)

    print(f"Red: {norm_r}, Green: {norm_g}, Blue: {norm_b}")
    print(f"Detected Color: {detected_color}")

try:
    while True:
        read_and_detect_color()
        time.sleep(1)
except KeyboardInterrupt:
    print("Program stopped")
