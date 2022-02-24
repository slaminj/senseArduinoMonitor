#include <SPI.h>
#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include "arduino_secrets.h"

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
char senseUser[] = SECRET_SENSE_ID;
char sensePass[] = SECRET_SENSE_PASS;

char server[] = "api.sense.com";
const char AUTH_URL[] = "/apiservice/api/v1/authenticate";
//char server[] = "httpbin.org";
//const char AUTH_URL[] = "/post";
int port = 443;
WiFiSSLClient wifi;
HttpClient client= HttpClient(wifi, server, port);
int status = WL_IDLE_STATUS;

//set interval for sending messages (milliseconds)
const long interval = 8000;
unsigned long previousMillis = 0;

int count = 0;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // attempt to connect to Wifi network:
  Serial.println("Startuping");
  while (status != WL_CONNECTED) {

    Serial.print("Attempting to connect to SSID: ");

    Serial.println(ssid);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:

    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:

//    delay(10000);

  }

  Serial.println("Connected to wifi");
  printWiFiStatus();
  Serial.println("\nStarting connection to server...");

  Serial.println("making POST request");
  String contentType = "application/x-www-form-urlencoded";
  String postData = "email=";
  postData+= senseUser;
  postData+="&password=";
  postData+=sensePass;

  client.post(AUTH_URL, contentType, postData);

  // read the status code and body of the response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Status code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);
  Serial.println("Startup done.");

  //todo - do JSON parsing next

  //if status 200, then save access_token
}

void loop() {
//  Serial.println("loop");
  // if there are incoming bytes available

  // from the server, read them and print them:

//  while (client.available()) {
//
//    char c = client.read();
//
//    Serial.write(c);
//
//  }

  // if the server's disconnected, stop the client:

//  if (!client.connected()) {
//
//    Serial.println();
//
//    Serial.println("disconnecting from server.");
//
//    client.stop();
//
//    // do nothing forevermore:
//
//    while (true);
//
//  }
}

void printWiFiStatus() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your board's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");
}
