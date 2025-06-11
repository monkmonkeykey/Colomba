#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCData.h>

char ssid[] = "Taller";          // Nombre de tu red Wi-Fi
char pass[] = "AscoSpock1@";     // Contraseña de tu red Wi-Fi

// Instancia UDP para enviar y recibir paquetes
WiFiUDP Udp;
const unsigned int localPort = 8888; // Puerto local para recibir mensajes OSC

OSCErrorCode error;

void setup() {
  Serial.begin(115200);
  Serial.println();

  // Conexión a la red Wi-Fi
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
   // Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());

  // Inicia UDP
  Udp.begin(localPort);
  Serial.print("Escuchando en el puerto: ");
  Serial.println(Udp.localPort());
}

// Función genérica para manejar mensajes
void handleMessage(OSCMessage &msg) {
  char address[50]; // Buffer para almacenar la dirección OSC
  msg.getAddress(address, 0); // Obtiene la dirección OSC y la guarda en el buffer

  int value = msg.getInt(0); // Obtiene el entero del mensaje
  Serial.print(address); // Imprime la dirección
  Serial.print(": ");
  Serial.println(value); // Imprime el valor recibido
}

void loop() {
  OSCBundle bundle;
  int size = Udp.parsePacket();

  if (size > 0) {
    while (size--) {
      bundle.fill(Udp.read());
    }

    if (!bundle.hasError()) {
      // Despachar mensajes para las direcciones /mensaje1 a /mensaje10
      bundle.dispatch("/a", handleMessage);
      bundle.dispatch("/b", handleMessage);
      bundle.dispatch("/c", handleMessage);
      bundle.dispatch("/d", handleMessage);
      bundle.dispatch("/e", handleMessage);
      bundle.dispatch("/f", handleMessage);
      bundle.dispatch("/g", handleMessage);
      bundle.dispatch("/h", handleMessage);
      bundle.dispatch("/i", handleMessage);
      bundle.dispatch("/j", handleMessage);
    } else {
      error = bundle.getError();
      Serial.print("Error: ");
      Serial.println(error);
    }
  }
  delay(30);
}
