#include <LiquidCrystal.h>
#include <LCDKeypad.h>
#include <Wire.h>
#include <DHT.h>

// Initialisation des #DEFINE
//
#define SLAVE_ADDRESS 0x03		// Adresse du bus I2C pour l'Arduino pilotant l'écran LCD
#define NO_KEY 900						// Valeur inférieure du LCD si aucune touche n'est pressée
#define KEY_SELECT 600				// Même chose pour la touche SELECT (la plus à geuche)
#define KEY_LEFT 300					// Même chose pour la touche gauche
#define KEY_DOWN 200					// Même chose pour la touche bas
#define KEY_UP 50							// Même chose pour la touche haut
#define KEY_RIGHT 0						// Même chose pour la touche droite
#define DHT_PIN 2							// Entrée digitale sur laquelle est branchée la sonde DHT11 ou DHT22
#define DHT_TYPE DHT22				// DHT11 ou DHT22 suivant le type de sonde température / humidité
#define W_LED_PIN 11					// GPIO qui commande la LED de WARNING
#define A_LED_PIN 12					// GPIO qui commande la LED d'ALERT
#define BUZZER_PIN 13					// GPIO qui commande le buzzer
#define FANS_PIN 3						// GPIO qui commande les ventilateurs (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LOOP_DELAY 100				// Temps d'attente avant de rcommencer le processing de la boucle principale
#define LCD_LIGHT 5000				// Temps d'allumage du LCD à la suite d'un événement
#define WARNING_UP 100				// Temps d'un beep du buzzer en type WARNING
#define WARNING_DOWN -5000		// Temps de pause entre deux beeps du buzzer en mode WARNING
#define BUZZER_INHIBIT 600000	// Temps de pause entre deux beeps du buzzer en mode WARNING
#define INHIBIT_PRESSED 500		// Valeur à comparer pour vérifier l'action du bouton INHIBIT
#define MEASURE_DELAY 10000		// Temps écoulé entre chaque prise de mesure des sondes
#define LCD_ANALOG_READ 0			// Entrée analogique à laquelle est connecté le mini clavier du LCD
#define INHIBIT_ANALOG_READ 1	// Entrée analogique à laquelle est connecté le bouton d'inhibition du buzzer
#define AIR_TEMP_HIGH 22			// Température maximale de l'air du système
#define AIR_TEMP_LOW 18				// Température minimale de l'air du système
#define AIR_TEMP_DELTA 1			// Différence par rapport aux maxima lors de l'action du feedback pour l'air du système


// Initialisation des variables globales
//
byte c_degree[8] = {							// Symbole des degrés pour l'écran LCD
	B01110,
	B10001,
	B10001,
	B01110,
	B00000,
	B00000,
	B00000,
	B00000
};
LCDKeypad lcd;										// Ecran LCD
DHT dht(DHT_PIN, DHT_TYPE);				// Sonde de température et d'hygrométrie de l'air
bool sysUp = true;								// Indique l'état général de l'unité hydroponique
bool warning = false;							// Indique si une alarme de type WARNING est en cours
int warningBeep;									// Indique l'état du buzzer en cas de WARNING, positive = buzzer ON period, negative = buzzer off period 
bool alert = false;								// Indique si une alarme de type ALERT est en cours
int lcdLight = LCD_LIGHT;					// Au début, on affiche ce qui se passe
int measureDelay = MEASURE_DELAY; // On prend une mesure provenant des sondes à intervalles définis
int myHeartbeat = 4;							// Au démarrage, on suppose que l'incrément du heartbeat est à zéro
long buzzerInhibit = 0;						// Coupe l'action du buzzer pendant la période définie par BUZZER_INHIBIT, pas activé par défaut 
bool buzzerVoid = false;					// Flag qui coupe complètement les alarmes sonores
int piCmd;												// Dernière commande reçue du  Raspberry Pi
float airTemperature;							// Variable qui stocke entre deux mesures la valeur lue pour la température de l'air
float airHumidity;								// Variable qui stocke entre deux mesures la valeur lue pour l'humidité de l'air

// Initialisation diverses de l'unité hydroponique avant d'entrer la boucle de contrôle principale
//
void setup(){

	// Crée le symbole degrés
	lcd.createChar(1, c_degree);

	// Important pour piloter le rétro-éclairage du LCD
	// La PIN 10 doit IMPERATIVEMENT rester sur la valeur LOW
	// pinMode de type INPUT - Rétro-éclairage allumé
	// pinMode de type OUTPUT - Rétro-éclairage éteint
	lcdBacklightInit();

	// Affiche le texte de bienvenue
  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("*** SYS BOOT ***");
 	lcd.setCursor(0, 1);

	// Prépare la communication I2C entre l'Arduino et le Raspberry
	Serial.begin(9600);
	Wire.begin(SLAVE_ADDRESS);
	Wire.onReceive(receiveI2C);
	Wire.onRequest(sendI2C);

	// Prépare la communication avec la sonde de température / humidité
	dht.begin();

	// Prépare la commande des ventilateurs
	pinMode(FANS_PIN, OUTPUT);
	analogWrite(FANS_PIN, 0);

	// Prépare la partie alarming
	pinMode(W_LED_PIN, OUTPUT);
	pinMode(A_LED_PIN, OUTPUT);
	pinMode(BUZZER_PIN, OUTPUT);
	digitalWrite(W_LED_PIN, LOW);
	digitalWrite(A_LED_PIN, LOW);
	digitalWrite(BUZZER_PIN, LOW);
}

// Boucle principale de régulation de l'unité hydroponique
//
void loop(){

	// Les lignes qui suivent contiennent les actions qui sont exécutées à chaque itération
	int key = getLCDKey();
	checkBuzzerInhibit();
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
			case 0x00:
				myHeartbeat = 65535;
				sysUp = true;
			break;
			// Commande 0x01 - Heartbeat
			case 0x01:
				myHeartbeat++;
			break;
			// Commande 0x02 - Afficher sur le LCD
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
			sendFloat(airHumidity);
			break;
		case 0x21:
			sendFloat(airTemperature);
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
	readValue = analogRead(LCD_ANALOG_READ);

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
	lcdLight = LCD_LIGHT;
	pinMode(10, INPUT);
}

// Active l'alarme de type WARNING
//
void warningOn(){
	warning = true;
	digitalWrite(W_LED_PIN, HIGH);
	warningBeep = WARNING_UP + LOOP_DELAY;
}

// Désctive l'alarme de type WARNING
//
void warningOff(){
	warning = false;
	digitalWrite(W_LED_PIN, LOW);
}

// Active l'alarme de type WARNING
//
void alertOn(){
	alert = true;
	digitalWrite(A_LED_PIN, HIGH);
	if(!buzzerVoid) digitalWrite(BUZZER_PIN, HIGH);
}

// Désctive l'alarme de type WARNING
//
void alertOff(){
	alert = false;
	digitalWrite(A_LED_PIN, LOW);
	digitalWrite(BUZZER_PIN, LOW);
}

// Vérifie si l'opérateur a actionné le bouton d'inhibition du buzzer d'alarme
// Si le bouton a été pressé, initialise le décompthe de l'inhibition et coupe le son
// Ne fait rien sinon
//
void checkBuzzerInhibit(){
	if(analogRead(INHIBIT_ANALOG_READ) > INHIBIT_PRESSED){
		buzzerInhibit = BUZZER_INHIBIT;
		digitalWrite(BUZZER_PIN, LOW);
	}
}

// Récolte les valeurs des différentes sondes connectées au système
//
bool getProbesValues(){
	airTemperature = dht.readTemperature();
	airHumidity = dht.readHumidity();
	return true;
}

// Implémentation des feedbacks suite aux paramètres de l'unité rapportés à la lecture des sondes
//
void provideFeedbacks(){
  lcd.clear();
	lcd.print("TEMP: ");
	lcd.print(airTemperature);
	lcd.write(1);
	lcd.print("C");
	lcd.setCursor(0, 1);
	lcd.print("HUMIDITY: ");
	lcd.print(airHumidity);
	lcd.print("% "); 
	if(warning && airTemperature < AIR_TEMP_HIGH - AIR_TEMP_DELTA){
		warningOff();
		analogWrite(FANS_PIN, 0);
	}
	if(warning && airTemperature > AIR_TEMP_HIGH + AIR_TEMP_DELTA) warningOff();
	if(airTemperature > AIR_TEMP_HIGH){
		warningOn();
		analogWrite(FANS_PIN, 255);
	}
	if(airTemperature < AIR_TEMP_LOW) warningOn();
}

// Procédure appelée à chaque itération de la boucle principale
// Vérifie l'état des compteurs d'événements par rapport à l'état du système
// et prend les mesures adéquates lors de transitions
//
void keepEventCounters(){

	// Décompte le temps qui s'écoule entre deux prises de mesures provenant des sondes
	// Si le temps est écoulé, on lit les valeurs renvoyées par les sondes et si tout s'est
	// bien passé, on déclenche les feedbacks et alarmes au besoin
	measureDelay -= LOOP_DELAY;
	if(measureDelay == 0){
		measureDelay = MEASURE_DELAY;
		if(getProbesValues()){
			provideFeedbacks();
		}
	}

	// Décompte le temps pendant lequel l'écran LCD est allumé
	// Si le temps est écoulé, coupe le rétro-éclairage
	if(lcdLight == LOOP_DELAY) lcdBacklightOff();
	if(lcdLight > 0) lcdLight -= LOOP_DELAY;

	// Vérifie si un événement de type WARNING est en cours
	// Si c'est le cas, maintient les variables d'état afin d'obtenir
	// des beeps courts comme définis dans la partie initialisation des constantes
	// Cette action n'est pas effective si une alarme est en cours (buzzer continu)
	// ou si le buzzer est inhibé par la touche adhoc
	if(warning && !alert && buzzerInhibit == 0 && !buzzerVoid){
		if(warningBeep == WARNING_UP) digitalWrite(BUZZER_PIN, HIGH);
		if(warningBeep == WARNING_DOWN) digitalWrite(BUZZER_PIN, LOW);
		if(warningBeep >= LOOP_DELAY){
			warningBeep -= LOOP_DELAY;
			if(warningBeep == 0) warningBeep = WARNING_DOWN;
		}
		else{
			warningBeep += LOOP_DELAY;
			if(warningBeep == 0) warningBeep = WARNING_UP;
		}
	}

	// Décompte le temps de l'inhibition du buzzer si nécessaire
	if(buzzerInhibit == LOOP_DELAY && alert && !buzzerVoid) digitalWrite(BUZZER_PIN, HIGH);
	if(buzzerInhibit > 0) buzzerInhibit -= LOOP_DELAY;
}
