
// Lots of code from here: http://forum.arduino.cc/index.php?topic=396450.0

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Example 3 - Receive with start- and end-markers

const byte numChars = 41;
char receivedChars[numChars];

boolean newData = false;

void setup() {
    Serial.begin(115200);
    Serial.println("<Arduino is ready>");
    pwm.begin();
    pwm.setPWMFreq(1600);
    for(int i=0; i<10; i++){
      pwm.setPWM(i,0,4096);
    }
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void showNewData() {
    if (newData == true) {
        Serial.println("This just in ... ");
        for(int i=0; i<10; i++) {
          char buffer[3];
          int idx = i*4;
          buffer[0] = receivedChars[idx];
          buffer[1] = receivedChars[idx+1];
          buffer[2] = receivedChars[idx+2];
          int n = 255 - atoi(buffer);
          Serial.println(n);
          pwm.setPWM(i,0,4096-n*16);
        }
        newData = false;
    }
}
