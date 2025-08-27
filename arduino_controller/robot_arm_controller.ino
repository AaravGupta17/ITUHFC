/*
  Robot Arm Controller Sketch

  This program listens for commands over the serial port to control a 3-axis
  robotic arm with a gripper.

  Hardware Assumptions:
  - 3 Stepper motors (Base, Shoulder, Elbow) controlled by drivers like A4988 or DRV8825.
  - 1 Servo motor for the gripper.
  - Arduino Uno or similar microcontroller.

  Recommended Libraries:
  - AccelStepper: For smooth, non-blocking control of the stepper motors.
    (Install from Arduino Library Manager)
  - Servo: Comes standard with the Arduino IDE.

  Serial Communication Protocol:
  Commands are sent as a string followed by a newline character ('\n').
  Format: <Identifier>,<Value>\n

  Identifiers:
  - 'B': Base motor
  - 'S': Shoulder motor
  - 'E': Elbow motor
  - 'G': Gripper servo

  Example Commands:
  - "B,90.5\n"  -> Move Base motor to 90.5 degrees.
  - "S,45.0\n"  -> Move Shoulder motor to 45.0 degrees.
  - "G,1\n"     -> Close the gripper (1 for close, 0 for open).
*/

#include <Servo.h>
// #include <AccelStepper.h> // Uncomment when you have the library installed

// --- Define Hardware Pins (Update with your actual wiring) ---
// Stepper Motor Pins
const int BASE_STEP_PIN = 2;
const int BASE_DIR_PIN = 5;
const int SHOULDER_STEP_PIN = 3;
const int SHOULDER_DIR_PIN = 6;
const int ELBOW_STEP_PIN = 4;
const int ELBOW_DIR_PIN = 7;

// Gripper Servo Pin
const int GRIPPER_SERVO_PIN = 9;

// --- Motor & Servo Objects ---
Servo gripperServo;
// AccelStepper baseStepper(AccelStepper::DRIVER, BASE_STEP_PIN, BASE_DIR_PIN);
// AccelStepper shoulderStepper(AccelStepper::DRIVER, SHOULDER_STEP_PIN, SHOULDER_DIR_PIN);
// AccelStepper elbowStepper(AccelStepper::DRIVER, ELBOW_STEP_PIN, ELBOW_DIR_PIN);


// --- Serial Communication Buffer ---
char serialBuffer[64];
int bufferPos = 0;

void setup() {
  Serial.begin(9600);
  Serial.println("Robot Arm Controller Initialized.");

  // Attach the servo
  gripperServo.attach(GRIPPER_SERVO_PIN);

  // TODO: Configure AccelStepper objects here
  // e.g., baseStepper.setMaxSpeed(1000);
  //       baseStepper.setAcceleration(500);
}

void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    char incomingChar = Serial.read();

    if (incomingChar == '\n') {
      // End of command, process it
      serialBuffer[bufferPos] = '\0'; // Null-terminate the string
      parseCommand(serialBuffer);
      bufferPos = 0; // Reset buffer
    } else {
      // Add character to buffer
      if (bufferPos < sizeof(serialBuffer) - 1) {
        serialBuffer[bufferPos++] = incomingChar;
      }
    }
  }

  // TODO: Run the steppers continuously
  // baseStepper.run();
  // shoulderStepper.run();
  // elbowStepper.run();
}

void parseCommand(char* command) {
  Serial.print("Received command: ");
  Serial.println(command);

  char identifier = command[0];
  float value = atof(command + 2); // Convert the part after the comma to a float

  switch (identifier) {
    case 'B':
      moveBase(value);
      break;
    case 'S':
      moveShoulder(value);
      break;
    case 'E':
      moveElbow(value);
      break;
    case 'G':
      setGripper(value == 1); // 1 for close, 0 for open
      break;
    default:
      Serial.println("Error: Unknown command identifier.");
      break;
  }
}

// --- Placeholder Functions ---

void moveBase(float angle) {
  Serial.print("Placeholder: Move Base to ");
  Serial.print(angle);
  Serial.println(" degrees.");
  // TODO: Implement actual motor control using AccelStepper
  // long steps = angle * (STEPS_PER_REVOLUTION / 360.0);
  // baseStepper.moveTo(steps);
}

void moveShoulder(float angle) {
  Serial.print("Placeholder: Move Shoulder to ");
  Serial.print(angle);
  Serial.println(" degrees.");
  // TODO: Implement actual motor control
}

void moveElbow(float angle) {
  Serial.print("Placeholder: Move Elbow to ");
  Serial.print(angle);
  Serial.println(" degrees.");
  // TODO: Implement actual motor control
}

void setGripper(bool close) {
  if (close) {
    Serial.println("Placeholder: Closing gripper.");
    // gripperServo.write(0); // Angle for closed position
  } else {
    Serial.println("Placeholder: Opening gripper.");
    // gripperServo.write(90); // Angle for open position
  }
}
