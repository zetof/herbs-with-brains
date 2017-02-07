#include <DHT.h>

// Initialisation des #DEFINE
//
#define ARDUINO_NAME "ARD2"	// Nom de l'Arduino utilisé pour s'enregistrer à la connexion avec le Raspberry
#define USB_SPEED 115200    // Vitesse de communication sur le port USB
#define USB_MAX_LENGTH 50		// Longueur maximale d'une phrase à envoyer au Raspberry
#define USB_MAX_PARAMS 5		// Nombre maximum de paramètres passés dans une commande provenant du Raspberry
#define FLOAT_MAX_LENGTH 10	// Longueur maximale d'un réel à transformer en string par la fonction dtostfr
#define DHT_PIN 2						// Entrée digitale sur laquelle est branchée la sonde DHT11 ou DHT22
#define DHT_TYPE DHT22			// DHT11 ou DHT22 suivant le type de sonde température / humidité
#define LED_RED_PIN 3				// GPIO qui commande la composante rouge des LEDs d'éclairage horticole (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LED_GREEN_PIN 5			// GPIO qui commande la composante verte des LEDs d'éclairage horticole (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LED_BLUE_PIN 6			// GPIO qui commande la composante bleue des LEDs d'éclairage horticole (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define RESET_PIN 7					// GPIO utilisée pour envoyer le signal de RESET de l'Arduino
#define LOOP_DELAY 100			// Temps d'attente avant de rcommencer le processing de la boucle principale
#define MEASURE_DELAY 10000	// Temps écoulé entre chaque prise de mesure des sondes

void readSerial();																																// Procédure qui écoute le port série à la fréquence du LOOP_DELAY (à placer dans la boucle principale)
void setRGB(int red, int green, int blue);																				// Procédure allumant l'éclairage à LEDs en fonction des valeurs RGB passées
void keepEventCounters();																													// Procédure qui dans la boucle principale déclenche les différents événements en fonction de leur programmation
void sendUSBValue(const char* parameter, int value);															// Procédure d'envoi d'un paramètre de type entier contrôlé par l'unité au Raspberry Pi
void sendUSBValue(const char* parameter, float value, int width, int precision);	// Procédure d'envoi d'un paramètre de type réel contrôlé par l'unité au Raspberry Pi

DHT dht(DHT_PIN, DHT_TYPE);				// Sonde de température et d'hygrométrie de l'air
bool sysUp = true;								// Indique l'état général de l'unité hydroponique
int measureDelay = MEASURE_DELAY; // On prend une mesure provenant des sondes à intervalles définis
int myHeartbeat = 4;							// Au démarrage, on suppose que l'incrément du heartbeat est à zéro
float airTemperature;							// Variable qui stocke entre deux mesures la valeur lue pour la température de l'air
float airHumidity;								// Variable qui stocke entre deux mesures la valeur lue pour l'humidité de l'air

// Initialisation diverses de l'unité hydroponique avant d'entrer la boucle de contrôle principale
//
void setup(){

	// Prépare la pin pour le reset de l'Arduino
	pinMode(RESET_PIN, OUTPUT);
	digitalWrite(RESET_PIN, LOW);

	// Prépare la communication vers le Raspberry Pi via le bus USB
	Serial.begin(USB_SPEED);

	// Prépare la communication avec la sonde de température / humidité
	dht.begin();

	// Prépare la commande de l'éclairage à LEDs et les éteint
	pinMode(LED_RED_PIN, OUTPUT);
	pinMode(LED_GREEN_PIN, OUTPUT);
	pinMode(LED_BLUE_PIN, OUTPUT);
	setRGB(0, 0, 0);
}

// Boucle principale de régulation de l'unité hydroponique
//
void loop(){

	// Les lignes qui suivent contiennent les actions qui sont exécutées à chaque itération
	readSerial();
	keepEventCounters();
	delay(LOOP_DELAY);
}


// Procédure allumant l'éclairage à LEDs en fonction des valeurs RGB passées
//
void setRGB(int red, int green, int blue){

	// Allume les rubans de LEDs suivants les paramètres rouge, vert et bleu passés
	analogWrite(LED_RED_PIN, red);
	analogWrite(LED_GREEN_PIN, green);
	analogWrite(LED_BLUE_PIN, blue);
}

// Ecoute le port série et analyse les messages reçus
//
void readSerial(){

	// Si il y a des données présentes sur le port série
	if(Serial.available() > 0){

		// On les lit (la fin est supposée toujours être délimitée par un "\n")
		String readData = Serial.readStringUntil('\n');

		// On extrait la position du premier séparateur afin d'isoler la commande
		// On prépare les index et la table de stockage pour la recherche des données
		int separator = readData.indexOf(':');
		int lastSeparator = separator + 1;
		int paramIndex = 0;
		String params[USB_MAX_PARAMS];

		// Si on a trouvé au moins une commande à analyser, on vérifie et on l'exécute si elle existe
		if(separator != -1){

			// On sépare la commande des données
			String command = readData.substring(0, separator);

			// On boucle pour récupérer les valeurs de paramètres associés à la commande
			while(separator != -1){

				// Cherche la valeur du paramètre suivant
				separator = readData.indexOf(':', lastSeparator);

				// On extrait la valeur située entre les deux séparateurs ou le dernier séparateur et la fin de la commande
				if(separator != -1){

					// On stocke la donnée, l'emplacement du dernier séparateur trouvé et on incrémente l'index des paramètres
					params[paramIndex] = readData.substring(lastSeparator, separator);
					lastSeparator = separator + 1;
					paramIndex++;
				}
				else params[paramIndex] = readData.substring(lastSeparator);
			}

			// Appelle les procédures correspondantes en fonction de la commande à exécuter
			if(command == "RGB") setRGB(params[0].toInt(), params[1].toInt(), params[2].toInt());
		}
	}
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
