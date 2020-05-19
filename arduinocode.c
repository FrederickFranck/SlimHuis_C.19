#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is aangesloten op digital pin 3
#define ONE_WIRE_BUS 3

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Piezo sensor is aangesloten op analoge pin 2
const int PIEZO_PIN = A2;

void setup()
{
    sensors.begin();
    Serial.begin(9600);
}

void loop()
{
    sensors.requestTemperatures();

    //print de temperatuur in Celsius
    Serial.print("Temp: ");
    Serial.print(sensors.getTempCByIndex(0));
    Serial.println("C")
    // Lees de piezo waarde en zet deze om naar een voltage
    int piezoADC = analogRead(PIEZO_PIN);
    float piezoV = piezoADC / 1023.0 * 5.0;
    // Print de voltage.
    Serial.print("Voltage :")
    Serial.println(piezoV);
    delay(500);
}
