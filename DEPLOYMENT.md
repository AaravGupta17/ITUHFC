# Deployment Guide: Raspberry Pi + Arduino

This document outlines the recommended architecture for running this robotic arm as a self-contained, autonomous unit and provides instructions for deployment.

## Architectural Proposal: Raspberry Pi + Arduino

The user request to convert the entire Python and C++ project to run on a single, bare-metal ATmega328P (the chip on an Arduino Uno) is not feasible due to the fundamental performance and memory limitations of that microcontroller.

-   **Memory:** The ATmega328P has only **32KB of Flash** for program storage and **2KB of RAM**. The Python logic, which includes kinematics, a strategic scheduler, and task definitions, requires a full Python interpreter and libraries that far exceed these limits.
-   **Performance:** The complex calculations for inverse kinematics and the logic for the strategy engine would run extremely slowly, if at all, on the 8-bit, 16MHz ATmega328P.

**The recommended professional solution is to use a "brain" and "muscle" architecture:**

1.  **The "Brain" (Raspberry Pi):** A Raspberry Pi (or a similar single-board computer) will run the high-level Python script (`python_controller.py`). It has ample processing power and memory to handle the strategic decisions, scheduling, and kinematics calculations.
2.  **The "Muscle" (Arduino):** The Arduino will continue to do what it does best: generate reliable, real-time signals to control the stepper motors and servo. It will receive simple commands from the Raspberry Pi over a USB serial connection.

This architecture is a standard and robust pattern in modern robotics. It combines the flexibility and power of a high-level language like Python with the reliability of a microcontroller for low-level hardware control.

## Deployment Instructions

To run this project on a Raspberry Pi:

### 1. Hardware Setup

-   Connect the Arduino to the Raspberry Pi using a USB cable.
-   Ensure the Raspberry Pi is powered and you can access its command line (e.g., via SSH).

### 2. Software Setup on Raspberry Pi

-   **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

-   **Install Dependencies:** Make sure you have Python 3 and pip installed. Then, install the required `pyserial` library:
    ```bash
    pip install -r requirements.txt
    ```

-   **Identify the Serial Port:** The Arduino will likely appear on a port named `/dev/ttyACM0` or `/dev/ttyUSB0`. You can find it by running `ls /dev/tty*` before and after plugging in the Arduino.

-   **Configure the Controller:** Open `python_controller.py` and ensure the `SERIAL_PORT` constant at the top of the file matches the port you identified.
    ```python
    # --- Configuration ---
    SERIAL_PORT = '/dev/ttyACM0' # <-- CHANGE THIS IF NEEDED
    BAUD_RATE = 9600
    # ...
    ```

### 3. Running the Robot

-   From the root of the project directory on your Raspberry Pi, simply run the main controller script:
    ```bash
    python3 python_controller.py
    ```

The robot will initialize and begin executing its mission autonomously, controlled by the Raspberry Pi.
