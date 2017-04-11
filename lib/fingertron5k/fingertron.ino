

#include <Servo.h>

Servo myservo;

int pos = 0;
int start = 120;
int endAngle = 174;
int delayTime = 5000;
bool hasPressed = false;

void setup() {
  myservo.attach(9);
}
void pressButton(){
  if(!hasPressed){
    for (pos = start; pos <= endAngle; pos += 1) {
      myservo.write(pos);              
      delay(15);                       
    }
    for (pos = endAngle; pos >= start; pos -= 1) { 
      myservo.write(pos);             
      delay(15);                       
    }
    hasPressed = true;
  }
}
void loop() {
  delay(delayTime);
  pressButton();
}
