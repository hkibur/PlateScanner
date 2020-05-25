#include <ArduinoJson.h>
#include <AFMotor.h>

#define TYPE_KEY "__ptype__"

#define READY_PACKET_TYPE "ready"

#define TRANSLATE_PACKET_TYPE "trans"
#define TRANSLATE_PACKET_X "x"
#define TRANSLATE_PACKET_Y "y"

#define STEPPER_SPEED 10

AF_Stepper x_motor(60, 1); // Ports M1 and M2
AF_Stepper y_motor(60, 2); // Ports M3 and M4

DynamicJsonDocument json_doc(512);

void send_packet(char *packet_type){
    json_doc[TYPE_KEY] = "ready";
    serializeJson(json_doc);
    Serial.println(); // Host client needs packets to be newline delimated
}

void send_ready_packet(){
    send_packet(READY_PACKET_TYPE);
}

void exec_translate_packet(){
    int x_amt = json_doc[TRANSLATE_PACKET_X];
    int y_amt = json_doc[TRANSLATE_PACKET_Y];
}

void setup(){
    Serial.being(9600);
    x_motor.setSpeed(STEPPER_SPEED);
    y_motor.setSpeed(STEPPER_SPEED);
    send_ready_packet(); // Generate "Ready signal"
}

void loop(){
    if(Serial.available() == 0){
        return;
    }

    deserializeJson(json_doc, Serial);

    switch(json_doc[TYPE_KEY]){
        case TRANSLATE_PACKET_TYPE: exec_translate_packet(); break;
    }
}