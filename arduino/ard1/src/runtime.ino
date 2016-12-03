#include <LiquidCrystal.h>
#include <LCDKeypad.h>
#include <Wire.h>
#include <DHT.h>

// Initialisation des #DEFINE
//
#define SLAVE_ADDRESS 0x03	// Adresse du bus I2C pour l'Arduino pilotant l'écran LCD
#define NO_KEY 900					// Valeur inférieure du LCD si aucune touche n'est pressée
#define KEY_SELECT 600			// Même chose pour la touche SELECT (la plus à geuche)
#define KEY_LEFT 300				// Même chose pour la touche gauche
#define KEY_DOWN 200				// Même chose pour la touche bas
#define KEY_UP 50						// Même chose pour la touche haut
#define KEY_RIGHT 0					// Même chose pour la touche droite
#define DHT_PIN 2						// Entrée digitale sur laquelle est branchée la sonde DHT11 ou DHT22
#define DHT_TYPE DHT22			// DHT11 ou DHT22 suivant le type de sonde température / humidité
#define LOOP_DELAY 500			// Temps d'attente avant de rcommencer le processing de la boucle principale

// Initialisation des constantes
//
const int LCD_LIGHT = getTimeIterations(5);	// Temps d'allumage du LCD à la suite d'un événement

// Initialisation des variables globales
//
byte c_degree[8] = {				// Symbole des degrés pour l'écran LCD
	B01110,
	B10001,
	B10001,
	B01110,
	B00000,
	B00000,
	B00000,
	B00000
};
LCDKeypad lcd;							// Ecran LCD
DHT dht(DHT_PIN, DHT_TYPE);	// Sonde de température et d'hygrométrie de l'air
bool sysUp = true;					// Indique l'état général de l'unité hydroponique
int lcdLight = 0;						// Au début, on affiche ce qui se passe
int myHeartbeat = 4;				// Au démarrage, on suppose que l'incrément du heartbeat est à zéro
int piCmd;									// Holds the last received command from the Raspberry Pi

// Initialisation diverses de l'unité hydroponique avant d'entrer la boucle de contrôle principale
//
void setup(){

	// Crée le symbole degrés
	//
	lcd.createChar(1, c_degree);

	// Important pour piloter le rétro-éclairage du LCD
	// La PIN 10 doit IMPERATIVEMENT rester sur la valeur LOW
	// pinMode de type INPUT - Rétro-éclairage allumé
	// pinMode de type OUTPUT - Rétro-éclairage éteint
	//
	lcdBacklightInit();

	// Affiche le texte de bienvenue
	//
  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("*** SYS BOOT ***");
 	lcd.setCursor(0, 1);

	// Prépare la communication I2C entre l'Arduino et le Raspberry
	//
	Serial.begin(9600);
	Wire.begin(SLAVE_ADDRESS);
	Wire.onReceive(receiveI2C);
	Wire.onRequest(sendI2C);

	// Prépare la communication avec la sonde de température / humidité
	//
	dht.begin();
}

// Boucle principale de régulation de l'unité hydroponique
//
void loop(){
	float t = getAirTemperature();
	float h = getAirHumidity();
  lcd.clear();
	lcd.print("TEMP: ");
	lcd.print(t);
	lcd.write(1);
	lcd.print("C");
	lcd.setCursor(0, 1);
	lcd.print("HUMIDITY: ");
	lcd.print(h);
	lcd.print("% "); 
	int key = getLCDKey();
	keepEventCounters();
	delay(LOOP_DELAY);
}

// Lit des données sur le bus I2C et les interprète suivant le type de commande
//
void receiveI2C(int byteCount){
	while(Wire.available()) {
		piCmd = Wire.read();
		switch(piCmd){
			// Commande 0x00 - Initialise l'Arduino
			//
			case 0x00:
				myHeartbeat = 65535;
				sysUp = true;
			break;
			// Commande 0x01 - Heartbeat
			//
			case 0x01:
				myHeartbeat++;
			break;
			// Commande 0x02 - Afficher sur le LCD
			//
			case 0x02:
				lcdBacklightOn();
				char c = Wire.read();
				for(int i =1; i< byteCount - 1;i++){
					char c = Wire.read();
					lcd.print(c);
				}
			break;
		}
	}
}

// Envoie des données sur le bus I2C et les interpète suivant le type de command
//
void sendI2C(){
	switch(piCmd){
		case 0x00:
			sendInt(myHeartbeat);
			break;
		case 0x20:
			sendFloat(getAirHumidity());
			break;
		case 0x21:
			sendFloat(getAirTemperature());
			break;
	}
}

// Envoie exactement un octet sur le bus I2C
//
void sendByte(byte value){
	Wire.write(value);
}

// Envoie exactement un enier (int = 2 octets)  sur le bus I2C
//
void sendInt(int value){
	Wire.write((byte*)&value, sizeof(int));
}

// Envoie un réel (float = 4 octets) sur le bus I2C dans une trame de 32 octets
//
void sendFloat(float value){
	Wire.write((byte*)&value, sizeof(float));
}

// Renvoie un code correspondant à le touche pressée sur l'écran LCD
// Le code original est un nombre analagique provenant d'un réseau de résistances
// La valeur récupérée n'est pas exacte mais peut fluctuer de quelques points
// C'est pourquoi on travaille par plages et non par valeur exacte
//
int getLCDKey(){
	int readValue;
	int realKey;

	// On lit la valeur analogique provenant du réseau de résistances
	readValue = analogRead(0);

	// Pas de touche enfoncée, pas d'action particulière à part le rapporter
	if(readValue > NO_KEY) realKey = NO_KEY;
	else{

		// Une touche a été enfoncée, on allume le LCD et on renvoie la touche correspondante
		lcdBacklightOn();
		if(readValue > KEY_SELECT) realKey = KEY_SELECT;
		else if(readValue > KEY_LEFT) realKey = KEY_LEFT;
		else if(readValue > KEY_DOWN) realKey = KEY_DOWN;
		else if(readValue > KEY_UP) realKey = KEY_UP;
		else realKey = KEY_RIGHT;
	}
	return realKey;
}

// Initialise le rétro-éclairage de l'écran LCD, allumé par défaut
//
void lcdBacklightInit(){
	digitalWrite(10, LOW);
	pinMode(10, INPUT);
}

// Eteint le rétro-éclairage de l'écran LCD
//
void lcdBacklightOff(){
	pinMode(10, OUTPUT);
}

// Allume le rétro-éclairage de l'écran LCD
//
void lcdBacklightOn(){
	lcdLight = 0;
	pinMode(10, INPUT);
}

// Renvoie la valeur de la température mesurée par la sonde DHT11 ou DHT22
//
float getAirTemperature(){
	return dht.readTemperature();
}

// Renvoie la valeur de l'humidité mesurée par la sonde DHT11 ou DHT22
//
float getAirHumidity(){
	return dht.readHumidity();
}

// Calcule le nombre d'itérations nécessaires à temporiser un event défini par une constante
// La valeur d'entrée est le temps de temporisation exprimé en secondes
// Le retour de la fonction donne le nombre d'itérations nécessaire par rapport au temps
// d'attente défini pour la boucle principale
//
int getTimeIterations(int seconds){
	return seconds * 1000 / LOOP_DELAY;
}

void keepEventCounters(){
	if(lcdLight < LCD_LIGHT) lcdLight++;
	else lcdBacklightOff();
}
