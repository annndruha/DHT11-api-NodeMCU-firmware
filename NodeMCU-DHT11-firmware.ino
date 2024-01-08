#include <ESP8266WiFi.h>
#include "DHT.h"

// =================================== NodeMCU weird pins
//static const uint8_t D0   = 16;
//static const uint8_t D1   = 5;
//static const uint8_t D2   = 4;
//static const uint8_t D3   = 0;
//static const uint8_t D4   = 2; LED_PIN
//static const uint8_t LED  = 2;
//static const uint8_t D5   = 14;
//static const uint8_t D6   = 12;
//static const uint8_t D7   = 13;
//static const uint8_t D8   = 15;
//static const uint8_t D9   = 3;
//static const uint8_t D10  = 1;

#define LED_PIN 2
#define DHT_PIN 2
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

// Setup wifi
const char *SSID = "YOUR_WIFI_SSID";
const char *PASSWORD = "YOUR_WIFI_PASSWORD";

// Setup api host
const char *HOST = "YOUR_DOMAIN_NAME";
const char FINGERPRINT[] PROGMEM = "SHA-1 Fingerprint	of your domain";
const int HTTPS_PORT = 443;

// Setup this device for api
const char *DEVICE_TOKEN = "SOME_TOKEN_BY_DHT11-api";
const int SEND_DELAY = 6000;


float temperature;
float humidity;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(DHT_PIN, INPUT);

  for (int i=0; i<5; i++){
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
    digitalWrite(LED_PIN, HIGH);
  }

  dht.begin();
  
  Serial.begin(9600);
  Serial.print("DEVICE_TOKEN: ");
  Serial.println(DEVICE_TOKEN);
  WiFi.mode(WIFI_OFF);        //Prevents reconnection issue (taking too long to connect)
  delay(1000);
  WiFi.mode(WIFI_STA);        //Only Station No AP, This line hides the viewing of ESP as wifi hotspot
  
  WiFi.begin(SSID, PASSWORD);     //Connect to your WiFi router
  Serial.println("");

  Serial.print("Connecting");
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  //If connection successful show IP address in serial monitor
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(SSID);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());  //IP address assigned to your ESP
}

//=======================================================================
//                    Main Program Loop
//=======================================================================
void loop() {  
  WiFiClientSecure httpsClient;    //Declare object of class WiFiClient

  Serial.println(HOST);

  Serial.printf("Using FINGERPRINT '%s'\n", FINGERPRINT);
  httpsClient.setFingerprint(FINGERPRINT);
  httpsClient.setTimeout(15000); // 15 Seconds
  delay(1000);
  
  Serial.print("HTTPS Connecting");
  int r=0; //retry counter
  while((!httpsClient.connect(HOST, HTTPS_PORT)) && (r < 30)){
      delay(100);
      Serial.print(".");
      r++;
  }
  if(r==30) {
    Serial.println("Connection failed");
  }
  else {
    Serial.println("Connected to web");
  }


  temperature = dht.readTemperature(); // Gets the values of the temperature
  humidity = dht.readHumidity(); // Gets the values of the humidity
  Serial.print("Temperature = ");
  Serial.print(temperature);
  Serial.print("\tHumidity = ");
  Serial.println(humidity);
  
  String Link;

  Link = "/create_measurement?device_token=" + String(DEVICE_TOKEN) + "&temperature=" + String(temperature) + "&humidity=" + String(humidity);

  Serial.print("Requesting URL: ");
  Serial.println(HOST);

  httpsClient.print(String("POST ") + Link + " HTTP/1.1\r\n" +
               "Host: " + HOST + "\r\n" +
               "Content-Type: application/json"+ "\r\n" + 
               "Connection: close\r\n\r\n");

  Serial.println("POST request sent");
                  
  while (httpsClient.connected()) {
    String line = httpsClient.readStringUntil('\n');
    if (line == "\r") {
      Serial.println("headers received");
      break;
    }
  }

  Serial.println("Server response (cutted):");
  Serial.println("==========");
  String line;
  if(httpsClient.available()) {        
    line = httpsClient.readStringUntil('\n');
    Serial.println(line);
  }
  Serial.println("==========");
  Serial.println("Delay for next post...");
  delay(SEND_DELAY - 1200);
}
