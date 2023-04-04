#include <Arduino.h>
#include <math.h>
#include <ArduinoUniqueID.h>

	
  int volumeSlider[] = {A0, A1, A2, A3};
  int volume[4];
  int matrixOut[] = {2, 3, 4, 5};
  int matrixIn[] = {6, 7, 8, 9};
  int keyboard[4][4];
  int keyboardModePin = 10;

void readVolumeSliders(){
  for(int i = 0; i < 4; i++){
    int vol = (double) analogRead(volumeSlider[i]);
    if(volume[i] <= vol -2 || volume[i] >= vol +2 || (volume[i] != vol && (vol == 0 || vol == 1023))){
        volume[i] = vol;
        char buffer[21];
        sprintf(buffer, "Volumeslider %i: %03i%%", i, (int) (vol / 1023.0f * 100));
        Serial.println(buffer);
      }
  }
}

void printKeyboard(){
  for(int i = 0; i < 4; i++){
     for(int j = 0; j < 4; j++){
        Serial.print(keyboard[i][j]);
     }
     Serial.print("\t");
  }
  Serial.println();    
  
}

void keyPressed(int i, int j){
    //printKeyboard();
    char buffer[17];
    sprintf(buffer, "KeyPressed (%i,%i)", i, j);
    Serial.println(buffer);
}

void keyReleased(int i, int j){
    char buffer[17];
    sprintf(buffer, "KeyReleased (%i,%i)", i, j);
    Serial.println(buffer);
}

void setup() {
  Serial.begin(9600);
   pinMode(keyboardModePin, INPUT_PULLUP);
  for(int i = 0; i < 4; i++){
     volume[i] = 0;
     pinMode(volumeSlider[i], INPUT);
     pinMode(matrixIn[i], INPUT_PULLUP);
     pinMode(matrixOut[i], OUTPUT);
  }
  
   for(int i = 0; i < 4; i++){
      for(int j = 0; j < 4; j++){
        keyboard[i][j] = 1;
      }
   }

    UniqueIDdump(Serial);
    Serial.print("UniqueID: ");
    for (size_t i = 0; i < UniqueIDsize; i++)
    {
      if (UniqueID[i] < 0x10)
        Serial.print("0");
      Serial.print(UniqueID[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
    

}

void readKeyboard(){
    for(int i = 0; i < 4; i++){
      digitalWrite(matrixOut[i], LOW);
      for(int j = 0; j < 4; j++){
        if(digitalRead(matrixIn[j]) == LOW && keyboard[j][i] == 1){
          keyboard[j][i] = 0;
          keyPressed(j, i);
        }else if(digitalRead(matrixIn[j]) == HIGH && keyboard[j][i] == 0){
          keyboard[j][i] = 1;
          keyReleased(j, i);
        }
      }
      digitalWrite(matrixOut[i], HIGH);
    }
}

void loop() {
  readVolumeSliders();
  readKeyboard();

  if(digitalRead(keyboardModePin) == HIGH){
      
  }
}