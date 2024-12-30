import RPi.GPIO as GPIO
import time

# Pin numbers for the GPIOs controlling the HMC253AQS24 (replace with actual GPIO pin numbers)
A_PIN = 17  # GPIO17 for A
B_PIN = 27  # GPIO27 for B
C_PIN = 22  # GPIO22 for C

# Setup GPIO
def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
    GPIO.setwarnings(False)

    # Setup control pins as outputs
    GPIO.setup(A_PIN, GPIO.OUT)
    GPIO.setup(B_PIN, GPIO.OUT)
    GPIO.setup(C_PIN, GPIO.OUT)

    # Initialize all control pins to LOW (default state)
    GPIO.output(A_PIN, GPIO.LOW)
    GPIO.output(B_PIN, GPIO.LOW)
    GPIO.output(C_PIN, GPIO.LOW)

# Function to trigger the RF switch based on control values
def trigger_rf_mux(control_values):
    """
    control_values is a list of 3 elements corresponding to A, B, and C
    Each element should be either 0 (LOW) or 1 (HIGH)
    """
    if len(control_values) != 3:
        raise ValueError("Control values list must have exactly 3 elements.")

    # Set the GPIOs according to the control values
    GPIO.output(A_PIN, GPIO.HIGH if control_values[0] else GPIO.LOW)
    GPIO.output(B_PIN, GPIO.HIGH if control_values[1] else GPIO.LOW)
    GPIO.output(C_PIN, GPIO.HIGH if control_values[2] else GPIO.LOW)

    # Add a small delay if needed (depending on your system timing)
    time.sleep(0.1)  # Adjust the delay based on timing requirements

# Function to cleanup GPIO after use
def cleanup_gpio():
    GPIO.cleanup()

# Function to get control values from user input
def get_user_input():
    """
    Prompt the user for control values for A, B, and C.
    Returns a list of 3 values corresponding to [A, B, C].
    """
    while True:
        try:
            # Get user input as integers and make sure they are either 0 or 1
            a = int(input("Enter control value for A (0 or 1): "))
            b = int(input("Enter control value for B (0 or 1): "))
            c = int(input("Enter control value for C (0 or 1): "))

            # Validate input values
            if a in [0, 1] and b in [0, 1] and c in [0, 1]:
                return [a, b, c]
            else:
                print("Invalid input! Please enter 0 or 1 for each value.")
        except ValueError:
            print("Invalid input! Please enter numeric values (0 or 1).")

# Main function to handle GPIO setup, user input, and triggering
if __name__ == "__main__":
    try:
        # Setup the GPIO pins
        setup_gpio()

        while True:
            # Get control values from user input
            control_values = get_user_input()
            print(f"Triggering RF Mux with control values: {control_values}")

            # Trigger the RF switch
            trigger_rf_mux(control_values)

            # Ask the user if they want to enter another set of values or exit
            again = input("Do you want to enter another set of control values? (y/n): ").lower()
            if again != 'y':
                break

    finally:
        # Clean up the GPIOs after the program finishes
        cleanup_gpio()
