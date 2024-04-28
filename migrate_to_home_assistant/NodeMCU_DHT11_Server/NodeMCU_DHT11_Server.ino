#include "ESP8266WiFi.h"
#include "ESP8266WebServer.h"
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

#define LED 2
#define DHTTYPE DHT11

DHT dht(D1, DHTTYPE);
ESP8266WebServer server(80);
const char* ssid = "wifi-name";
const char* password = "password";

void setup() {
  pinMode(D1, INPUT);
  dht.begin();

  Serial.begin(9600);
  Serial.println("Start...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Non Connecting to WiFi..");
  } else {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    server.on("/temperature", temperature);
    server.on("/humidity", humidity);
    server.on("/uptime", uptime);
    server.on("/", handleRootPath);
    server.onNotFound(handleNotFound);
    server.begin();
    Serial.println("Server listening");
  }
}

void loop() {
  server.handleClient();
}

void temperature() {
  float temperature = dht.readTemperature();
  String response = String(temperature);
  server.send(200, "text/plain", response);
}


void humidity() {
  float humidity = dht.readHumidity();
  String response = String(humidity);
  server.send(200, "text/plain", response);
}

String getUptime(){
  unsigned long sec = millis() / 1000;
  unsigned long min = sec / 60;
  unsigned long hr = min / 60;
  unsigned long days = hr / 24;
  sec %= 60;
  min %= 60;
  hr %= 24;
  String response = String(days) + "d " +  String(hr) + ":" + String(min) + ":" + String(sec);
  return response;
}

void uptime() {
  server.send(200, "text/plain", getUptime());
}

void handleRootPath() {
  String response = """<h3>Hello from home NodeMCU DHT11 sensor!</h3>""" \
                    """Methods:""" \
                    """<br><a href=\"/temperature\">/temperature</a>  (""" + String(dht.readTemperature()) + ")" + \
                    """<br><a href=\"/humidity\">/humidity</a>  (""" + String(dht.readHumidity()) + ")" + \
                    """<br><a href=\"/uptime\">/uptime</a>  (""" + String(getUptime()) + ")";
  server.send(200, "text/html", response);
}


void handleNotFound() {
  String response ="""<p>Hello from home NodeMCU DHT11 sensor!</p>""" \
                   """<p><a href=\"/\">Go to main page</a></p>""";
  server.send(404, "text/html", response);
}
