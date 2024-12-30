import time
import board
import busio
import adafruit_tcs34725

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create a sensor object
sensor = adafruit_tcs34725.TCS34725(i2c)

# Set sensor integration time (optional, default is 2.4ms)
sensor.integration_time = 50  # You can set it between 2.4ms and 614ms

# Set gain (optional, default is 1x)
sensor.gain = 16  # Options: 1x, 4x, 16x, 60x

# Enable LED (optional)
sensor.led = True

# Function to get color data
def read_color():
    # Read the color values
    r, g, b, c = sensor.color_raw

    # Get the color temperature in Kelvin
    color_temp = sensor.color_temperature

    # Get the Lux value
    lux = sensor.lux

    print(f"Red: {r}, Green: {g}, Blue: {b}, Clear: {c}")
    print(f"Color Temperature: {color_temp} K")
    print(f"Lux: {lux} lux")

try:
    while True:
        read_color()
        time.sleep(1)
except KeyboardInterrupt:
    print("Program stopped")
