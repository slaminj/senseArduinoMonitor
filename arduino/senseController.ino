#include <SPI.h>
#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
//#include <Arduino_JSON.h>
#include <ArduinoJson.h>
#include "arduino_secrets.h"

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
char senseUser[] = SECRET_SENSE_ID;
char sensePass[] = SECRET_SENSE_PASS;

const char server[] = "api.sense.com";
const char AUTH_URL[] = "/apiservice/api/v1/authenticate";
const char socket[] = "clientrt.sense.com";
String socketURL = "/monitors/";

//char server[] = "httpbin.org";
//const char AUTH_URL[] = "/post";
int port = 443;
WiFiSSLClient wifi;
HttpClient client= HttpClient(wifi, server, port);
WebSocketClient wsClient = WebSocketClient(wifi, socket, port);
int status = WL_IDLE_STATUS;

String SENSE_ACCESS_TOKEN = "none";
String SENSE_MONITOR_ID = "none";


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

}

void loop() {
  //if token - get data
  if (SENSE_ACCESS_TOKEN != "none") {
    Serial.println("starting WebSocket client");
    wsClient.begin(socketURL);

    while (wsClient.connected()) {
      int messageSize = wsClient.parseMessage();
      String message = "";
      if (messageSize > 0) {
          Serial.print("Received a message:");
          message = wsClient.readString();
          Serial.println(message);
          StaticJsonDocument<128> messageData;
          DeserializationError err = deserializeJson(messageData, message);
          if (err) {
            Serial.print(F("deserializeJson() failed with code "));
            Serial.println(err.f_str());
          }
//          JSONVar messageData = JSON.parse(message);
          Serial.println(messageData["type"].as<const char*>());
          const char* mType = messageData["type"];
          Serial.print("mType: ");
          Serial.println(mType);
//          ?????
//          if (!mType){
//            Serial.println("try to recover string");
//            int index = message.indexOf("d_w");
//            String subMessage = message.substring(index);
//            String newMessage = "{\"payload\":{";
//            newMessage += subMessage;
//            messageData = JSON.parse(newMessage);
//            Serial.print("newMessage: ");
//            Serial.println(messageData);
//            mType = "realtime_update";
//          }
//          if (mType == "realtime_update") {
//            Serial.print("Received a realtime_update: ");
//            Serial.println(messageData);
//            int solar = messageData["payload"]["d_solar_w"];
//            int grid = messageData["payload"]["d_w"];
//            int avail = solar - grid;
//            Serial.print("solar: ");
//            Serial.println(solar);
//            Serial.print("grid: ");
//            Serial.println(grid);
//            Serial.print("avail: ");
//            Serial.println(avail);
//            Serial.println("Wait 1s for next message");
//            delay(1000);
//          }
       }
      
       // wait 5 seconds
      //parse data
      //get difference
      
     }
  }
  else {
    authenticate();
  }
  
}

void authenticate() {
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
  
  if (statusCode == 200) {
    StaticJsonDocument<192> htmlResponse;
    DeserializationError err = deserializeJson(htmlResponse, response);
//    JSONVar htmlResponse = JSON.parse(response);
    SENSE_ACCESS_TOKEN = htmlResponse["access_token"].as<String>();
    SENSE_MONITOR_ID = htmlResponse["monitors"][0]["id"].as<String>();
    constructWebSocketURL();
  }
  else {
    Serial.print("Authentication Failed: ");
    Serial.println(statusCode);
  }
}

void constructWebSocketURL() {
  //wss://clientrt.sense.com/monitors/213413/realtimefeed?access_token=t1.v2.eyJhbGciOiJIUzUxMiJ9.&sense_device_id=ldv..55&sense_protocol=8&sense_client_type=web
  socketURL += SENSE_MONITOR_ID;
  socketURL += "/realtimefeed?access_token=";
  socketURL += SENSE_ACCESS_TOKEN;
//  socketURL += "&sense_device_id=ldvhhsf2ehhfagv49g8r8vuunt7xgq2zafo7egjojhv9ljre5acvjkuvd7ugyemezcvdmg795n5qkipaungw2i38ptjmjjxz8se6hbiusmyi122baq1ow3g7z799f055&sense_protocol=8&sense_client_type=web";
//socketURL += "&sense_protocol=8&sense_client_type=web";
  Serial.print("WebSocketURL: ");
  Serial.println(socketURL);
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
