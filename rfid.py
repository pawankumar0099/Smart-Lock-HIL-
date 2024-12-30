import RPi.GPIO as GPIO
import time

# Set up the GPIO mode
GPIO.setmode(GPIO.BOARD)

# Define GPIO pins
pin1 = 11
pin2 = 13
pin3 = 15

# Set up pins as output
GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)
GPIO.setup(pin3, GPIO.OUT)

#GPIO.output(pin1,0)
#GPIO.output(pin2,0)
#GPIO.output(pin3,0)

# Function to set GPIO pins based on binary input
def set_gpio_pins(value):
    # Convert value to binary and set the pins accordingly
    bin_value = format(value, '03b')  # Convert value to a 3-bit binary string
   # print(f"Setting GPIO pins to: {bin_value}")
    print(bin_value[0])
    GPIO.output(pin1, int(bin_value[0]))  # Set pin1 (MSB)
    GPIO.output(pin2, int(bin_value[1]))  # Set pin2
    GPIO.output(pin3, int(bin_value[2]))  # Set pin3 (LSB)

try:
    while True:
        # Ask user for input
        user_input = input("Enter a number between 0 and 7 to toggle GPIO pins: ")
        if user_input.isdigit():
            value = int(user_input)
            if 0 <= value <= 7:
                set_gpio_pins(value)
            else:
                print("Please enter a number between 0 and 7.")
        else:
            print("Invalid input. Please enter a number.")
        
        # Sleep for a short time before the next iteration
        time.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted")

finally:
    # Clean up GPIO settings before exiting
    GPIO.cleanup()

