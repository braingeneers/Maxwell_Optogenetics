
/****************************************************************************** 
MCP4725 Thorlabs Waveforms
Braingeneers
03/04/2022 

Description: 
This sketch takes data from a lookup table to provide  waveforms to 
be generated by the MCP4725 DAC. 
DAC // -32,768 to 32,767
*******************************************************************************/


#include "SerialTransfer.h"
#include <Wire.h>

#define MCP4725_ADDR 0x60   
#define TRUE 1
#define FALSE 0


int lookup = 0;//varaible for navigating through the tables
SerialTransfer myTransfer;

struct __attribute__((__packed__)) STRUCT {
  uint16_t intensity;
  int16_t wav[64]; 
  bool select;
} position;

// MaxWell Input
int analogPin = A0; 
int MaxWell_Toggle = 0;

void setup() {
  Serial.begin(115200);
  myTransfer.begin(Serial);
  Wire.begin();

  // Set A2 and A3 as Outputs to make them our GND and Vcc,
  //which will power the MCP4725
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
  digitalWrite(A2, LOW);//Set A2 as GND
  digitalWrite(A3, HIGH);//Set A3 as Vcc

   while(!myTransfer.available());
   myTransfer.rxObj(position); 
   myTransfer.sendDatum((position));


//else if(myTransfer.status < 0)
//  {
//    Serial.print("ERROR: ");
//
//    if(myTransfer.status == -1)
//      Serial.println(F("CRC_ERROR"));
//    else if(myTransfer.status == -2)
//      Serial.println(F("PAYLOAD_ERROR"));
//    else if(myTransfer.status == -3)
//      Serial.println(F("STOP_BYTE_ERROR"));
//  }

//     //if(myTransfer.available()) {};
//     myTransfer.rxObj(data); //            wave = (char*) myTransfer.packet.rxBuff;
//     Serial.print("Bytes Read:");
//     Serial.println(myTransfer.bytesRead);
//     Serial.print("Data:");
//     Serial.println(data.z);
//     Serial.println(data.y);          

     
//   data = {'f', 4.2};
//   Serial.println(data.z);
//   Serial.println(data.y);


}


void loop()
{

 MaxWell_Toggle = analogRead(analogPin);
 
if (myTransfer.available()) {
    myTransfer.rxObj(position); 
    myTransfer.sendDatum((position));
  }


      Wire.beginTransmission(MCP4725_ADDR);
      Wire.write(64);

if(MaxWell_Toggle > 0){

if (position.select == TRUE){
      Wire.write(position.wav[lookup] >> 4);        // the 8 most significant bits...
      Wire.write((position.wav[lookup] & 0b1111) << 4); // the 4 least significant bits...
      lookup = (lookup + 1) & 63; // (size-1) //127 //255; //& 511; //modulo 255
      //delay(delayTime);
}else if (position.select == FALSE){
       lookup = 0;
       Wire.write(position.intensity >> 4);        // the 8 most significant bits...
       Wire.write((position.intensity & 0b1111) << 4);
}
} else {
      lookup = 0;
      Wire.write(0 >> 4);        // the 8 most significant bits...
      Wire.write((0 & 0b1111) << 4);
}

Wire.endTransmission(); 

delay(1);
      
}