#include <DHT.h>

// Initialisation des #DEFINE
//
#define ARDUINO_NAME "ARD2"	// Nom de l'Arduino utilisé pour s'enregistrer à la connexion avec le Raspberry
#define USB_MAX_LENGTH 50		// Longueur maximale d'une phrase à envoyer au Raspberry
#define FLOAT_MAX_LENGTH 10	// Longueur maximale d'un réel à transformer en string par la fonction dtostfr
#define DHT_PIN 2						// Entrée digitale sur laquelle est branchée la sonde DHT11 ou DHT22
#define DHT_TYPE DHT22			// DHT11 ou DHT22 suivant le type de sonde température / humidité
#define LED_RED_PIN 3				// GPIO qui commande la composante rouge des LEDs d'éclairage horticole (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LED_GREEN_PIN 5			// GPIO qui commande la composante verte des LEDs d'éclairage horticole (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LED_BLUE_PIN 6			// GPIO qui commande la composante bleue des LEDs d'éclairage horticole (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LOOP_DELAY 100			// Temps d'attente avant de rcommencer le processing de la boucle principale
#define MEASURE_DELAY 10000	// Temps écoulé entre chaque prise de mesure des sondes

void keepEventCounters();																													// Procédure qui dans la boucle principale déclenche les différents événements en fonction de leur programmation
void sendUSBValue(const char* parameter, int value);															// Procédure d'envoi d'un paramètre de type entier contrôlé par l'unité au Raspberry Pi
void sendUSBValue(const char* parameter, float value, int width, int precision);	// Procédure d'envoi d'un paramètre de type réel contrôlé par l'unité au Raspberry Pi

DHT dht(DHT_PIN, DHT_TYPE);				// Sonde de température et d'hygrométrie de l'air
bool sysUp = true;								// Indique l'état général de l'unité hydroponique
int measureDelay = MEASURE_DELAY; // On prend une mesure provenant des sondes à intervalles définis
int myHeartbeat = 4;							// Au démarrage, on suppose que l'incrément du heartbeat est à zéro
float airTemperature;							// Variable qui stocke entre deux mesures la valeur lue pour la température de l'air
float airHumidity;								// Variable qui stocke entre deux mesures la valeur lue pour l'humidité de l'air

// Prépare les valeurs initiales de LEDs
int red = 0;
int green = 0;
int blue = 0;

// Initialisation diverses de l'unité hydroponique avant d'entrer la boucle de contrôle principale
//
void setup(){

	// Prépare la communication vers le Raspberry Pi via le bus USB
	Serial.begin(115200);

	// Prépare la communication avec la sonde de température / humidité
	dht.begin();

	// Prépare la commande des ventilateurs
	pinMode(LED_RED_PIN, OUTPUT);
	pinMode(LED_GREEN_PIN, OUTPUT);
	pinMode(LED_BLUE_PIN, OUTPUT);
	analogWrite(LED_RED_PIN, 0);
	analogWrite(LED_GREEN_PIN, 0);
	analogWrite(LED_BLUE_PIN, 0);
}

// Boucle principale de régulation de l'unité hydroponique
//
void loop(){

	// Initialise l'état des LEDs d'éclairage
	analogWrite(LED_RED_PIN, red);
	analogWrite(LED_GREEN_PIN, green);
	analogWrite(LED_BLUE_PIN, blue);

	// Les lignes qui suivent contiennent les actions qui sont exécutées à chaque itération
	keepEventCounters();
	delay(LOOP_DELAY);
}

// Récolte les valeurs des différentes sondes connectées au système
//
bool getProbesValues(){
	airTemperature = dht.readTemperature();
	airHumidity = dht.readHumidity();
	sendUSBValue("AIR_TEMP", airTemperature, 5, 2);
	sendUSBValue("AIR_HUM", airHumidity, 5, 2);
	return true;
}

// Implémentation des feedbacks suite aux paramètres de l'unité rapportés à la lecture des sondes
//
void provideFeedbacks(){
}

// Procédure qui envoie un paramètre de type entier au Raspberry
// La phrase envoyée est du type ARDUINO_NAME:parameter:value
//
void sendUSBValue(const char* parameter, int value){
	char stringToSend[USB_MAX_LENGTH] = "";
	snprintf(stringToSend, USB_MAX_LENGTH, "%s:%s:%d", ARDUINO_NAME, parameter, value);
	Serial.println(stringToSend);
}

// Procédure qui envoie un paramètre de type réel au Raspberry
// La conversion se fait par la fonction dtostfr car le format %f de la commande snprintf n'est pas supporté par l'Arduino
// Le paramètre width donne la longueur totale du float converti, en incluant le signe, la virgule et les décimaux
// Le paramètre precision donne le nombre de chiffres derrière la virgule
// La phrase envoyée est du type ARDUINO_NAME:parameter:value
//
void sendUSBValue(const char* parameter, float value, int width, int precision){
	char stringToSend[USB_MAX_LENGTH] = "";
	char float2String[FLOAT_MAX_LENGTH] = "";
	dtostrf(value, width, precision, float2String); 
	snprintf(stringToSend, USB_MAX_LENGTH, "%s:%s:%s", ARDUINO_NAME, parameter, float2String);
	Serial.println(stringToSend);
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
}
