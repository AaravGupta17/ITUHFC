/*
  Robot Arm Controller Sketch

  This program listens for commands over the serial port to control a 3-axis
  robotic arm with a gripper.

  ====================================================================
  HOW TO MEET THE 2-MINUTE TIME LIMIT
  ====================================================================
  The speed of the robot is determined by how fast the physical motors can move.
  The Python "brain" script is very fast, but the Arduino needs to be told how
  fast it is allowed to run the motors.

  This is done using the AccelStepper library. You MUST use this library for
  high-speed movements.

  The key parameters to tune are:
  - setMaxSpeed(): The maximum speed the motor can run without stalling.
  - setAcceleration(): How quickly the motor can ramp up to that max speed.

  You will need to EXPERIMENT with these values for your specific motors and arm
  weight. Start with low values, and gradually increase them until the motors
  start to skip steps, then reduce the values slightly. Higher values mean a
  faster mission time. I have added example values in the setup() function below.
  ====================================================================

  Recommended Libraries:
  - AccelStepper: For smooth, non-blocking control of the stepper motors.
    (Install from Arduino Library Manager)
  - Servo: Comes standard with the Arduino IDE.

  Serial Communication Protocol:
  Format: <Identifier>,<Value>\n (e.g., "B,90.5\n", "G,1\n")
*/

#include <Servo.h>
#include <AccelStepper.h>

// --- Define Hardware Pins (Update with your actual wiring) ---
const int BASE_STEP_PIN = 2;
const int BASE_DIR_PIN = 5;
const int SHOULDER_STEP_PIN = 3;
const int SHOULDER_DIR_PIN = 6;
const int ELBOW_STEP_PIN = 4;
const int ELBOW_DIR_PIN = 7;
const int GRIPPER_SERVO_PIN = 9;

// Define motor interface type. 1 = A4988/DRV8825 driver
#define motorInterfaceType 1

// --- Motor & Servo Objects ---
Servo gripperServo;
AccelStepper baseStepper(motorInterfaceType, BASE_STEP_PIN, BASE_DIR_PIN);
AccelStepper shoulderStepper(motorInterfaceType, SHOULDER_STEP_PIN, SHOULDER_DIR_PIN);
AccelStepper elbowStepper(motorInterfaceType, ELBOW_STEP_PIN, ELBOW_DIR_PIN);

// --- Serial Communication Buffer ---
char serialBuffer[64];
int bufferPos = 0;

void setup() {
  Serial.begin(9600);
  Serial.println("Robot Arm Controller Initialized.");

  gripperServo.attach(GRIPPER_SERVO_PIN);

  // === SPEED CONFIGURATION ===
  // These values are examples. You MUST tune them for your robot.
  baseStepper.setMaxSpeed(1000);
  baseStepper.setAcceleration(500);

  shoulderStepper.setMaxSpeed(1000);
  shoulderStepper.setAcceleration(500);

  elbowStepper.setMaxSpeed(1000);
  elbowStepper.setAcceleration(500);
}

void loop() {
  // Check for incoming serial data to process new commands
  if (Serial.available() > 0) {
    char incomingChar = Serial.read();
    if (incomingChar == '\n') {
      serialBuffer[bufferPos] = '\0';
      parseCommand(serialBuffer);
      bufferPos = 0;
    } else {
      if (bufferPos < sizeof(serialBuffer) - 1) {
        serialBuffer[bufferPos++] = incomingChar;
      }
    }
  }

  // This is the most important part for speed:
  // The .run() functions must be called as often as possible in the loop.
  // They will move the motors towards their target angles smoothly.
  baseStepper.run();
  shoulderStepper.run();
  elbowStepper.run();
}

void parseCommand(char* command) {
  Serial.print("Received command: ");
  Serial.println(command);

  char identifier = command[0];
  float value = atof(command + 2);

  switch (identifier) {
    case 'B': moveBase(value); break;
    case 'S': moveShoulder(value); break;
    case 'E': moveElbow(value); break;
    case 'G': setGripper(value == 1); break;
    default: Serial.println("Error: Unknown command identifier."); break;
  }
}

// --- Motor Control Functions ---

void moveBase(float angle) {
  // Assuming 200 steps per revolution and 1x microstepping
  long steps = angle * (200.0 / 360.0);
  baseStepper.moveTo(steps);
}

void moveShoulder(float angle) {
  long steps = angle * (200.0 / 360.0);
  shoulderStepper.moveTo(steps);
}

void moveElbow(float angle) {
  long steps = angle * (200.0 / 360.0);
  elbowStepper.moveTo(steps);
}

void setGripper(bool close) {
  if (close) {
    gripperServo.write(0); // Angle for closed position
  } else {
    gripperServo.write(90); // Angle for open position
  }
}
