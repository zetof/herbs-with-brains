#include <Arduino.h>

// Initialisation des #DEFINE
//
#define ARDUINO_NAME "ARD1"		// Nom de l'Arduino utilisé pour s'enregistrer à la connexion avec le Raspberry
#define USB_SPEED 115200			// Vitesse de communication sur le port USB
#define USB_MAX_LENGTH 20			// Longueur maximale d'une phrase à envoyer au Raspberry
#define LCD_ANALOG_READ 0			// Entrée analogique à laquelle est connecté le mini clavier du LCD
#define NO_KEY 900						// Valeur inférieure du LCD si aucune touche n'est pressée
#define KEY_SELECT 600				// Même chose pour la touche SELECT (la plus à geuche)
#define KEY_LEFT 300					// Même chose pour la touche gauche
#define KEY_DOWN 200					// Même chose pour la touche bas
#define KEY_UP 50							// Même chose pour la touche haut
#define KEY_RIGHT 0						// Même chose pour la touche droite
#define LOOP_DELAY 100				// Temps d'attente avant de rcommencer le processing de la boucle principale
#define KEY_WAIT 1000					// Temps d'attente avant la répétition d'une touche
#define KEY_REPEAT 200				// Temps entre la répétition d'une même touche lorsqu'elle reste enfoncée
#define MEASURE_DELAY 10000		// Temps écoulé entre chaque prise de mesure des sondes

void getLCDKey();																						// Procédure dans la boucle principale qui scanne la pression sur une touche du clavier LCD
void keepEventCounters();																		// Procédure qui dans la boucle principale déclenche les différents événements en fonction de leur programmation
void sendUSBCommand(const char* parameter, bool withValue);	// Procédure d'envoi d'une commande vers le Raspberry Pi
void sendUSBValue(const char* parameter, int value);				// Procédure d'envoi d'un paramètre de type entier contrôlé par l'unité au Raspberry Pi
void sendUSBValue(const char* parameter, float value);			// Procédure d'envoi d'un paramètre de type réel contrôlé par l'unité au Raspberry Pi

bool sysUp = true;								// Indique l'état général de l'unité hydroponique
int measureDelay = MEASURE_DELAY; // On prend une mesure provenant des sondes à intervalles définis
int myHeartbeat = 4;							// Au démarrage, on suppose que l'incrément du heartbeat est à zéro
int keyPressed = NO_KEY;					// Stocke la dernière touche pressée sur le LCD
int keyWait = 0;									// Temps avant la répétition d'une touche enfoncée
int keyRepeat = 0;								// Temps entre deux événements de touche lorsque la même touche est toujours maintenue pressée

// Initialisation diverses de l'unité hydroponique avant d'entrer la boucle de contrôle principale
//
void setup(){

	// Prépare la communication vers le Raspberry Pi via le bus USB
	Serial.begin(USB_SPEED);
}

// Boucle principale de régulation de l'unité hydroponique
//
void loop(){

	// Les lignes qui suivent contiennent les actions qui sont exécutées à chaque itération
	getLCDKey();
	keepEventCounters();
	delay(LOOP_DELAY);
}

// Renvoie un code correspondant à la touche pressée sur l'écran LCD
// Le code original est un nombre analogique provenant d'un réseau de résistances
// La valeur récupérée n'est pas exacte mais peut fluctuer de quelques points
// C'est pourquoi on travaille par plages et non par valeur exacte
//
void getLCDKey(){
	int readValue;
	int realKey;

	// On lit la valeur analogique provenant du réseau de résistances
	readValue = analogRead(LCD_ANALOG_READ);

	// On traduit la valeur de la touche à partir dela valeur lue
	if(readValue > NO_KEY) realKey = NO_KEY;
	else if(readValue > KEY_SELECT) realKey = KEY_SELECT;
	else if(readValue > KEY_LEFT) realKey = KEY_LEFT;
	else if(readValue > KEY_DOWN) realKey = KEY_DOWN;
	else if(readValue > KEY_UP) realKey = KEY_UP;
	else realKey = KEY_RIGHT;

	// Si la touche pressée est différente de la touche précédemment pressée
	if(realKey != keyPressed){

		// On réinitialise les variables de contrôle de touche
		keyPressed = realKey;
		keyWait = KEY_WAIT;
		keyRepeat = 0;

		// Si une touche a été pressée, on l'envoie via le port USB
		if(realKey != NO_KEY)	sendUSBValue("KEY", realKey);
	}

	// La touche pressée est la même que précédemment et si c'est une vraie action
	else if(realKey != NO_KEY){

		// On est dans la phase du premier cycle
		if(keyWait > 0)	keyWait -= LOOP_DELAY;

		// On est dans les cycles suivants
		else{
			
			// On n'est pas encore au bout d'un cycle de répétition
			if(keyRepeat > 0)	keyRepeat -= LOOP_DELAY;

			// On est au bout d'un cycle de répétition donc on envoie la touche et on réinitialise la variable de contrôle
			else{
				keyRepeat = KEY_REPEAT;
				sendUSBValue("KEY", realKey);
			}	
		}
	}
}

// Récolte les valeurs des différentes sondes connectées au système
//
bool getProbesValues(){
	return true;
}

// Implémentation des feedbacks suite aux paramètres de l'unité rapportés à la lecture des sondes
//
void provideFeedbacks(){
}

// Fonction qui formatte la commande à envoyer au Raspberry Pi hors valeur du paramètre
// et l'envoie sur le bus série USB sans fin de phrase. Le paramètre doit être envoyé après
//
void sendUSBCommand(const char* parameter, bool withValue){
	char stringToSend[USB_MAX_LENGTH] = "";
	if(withValue){
		snprintf(stringToSend, USB_MAX_LENGTH, "%s:%s:", ARDUINO_NAME, parameter);
		Serial.print(stringToSend);
	}
	else{
		snprintf(stringToSend, USB_MAX_LENGTH, "%s:%s", ARDUINO_NAME, parameter);
		Serial.println(stringToSend);
	}
}

// Procédure qui envoie un paramètre de type entier au Raspberry
// La phrase envoyée est du type ARDUINO_NAME:parameter:value
//
void sendUSBValue(const char* parameter, int value){
	sendUSBCommand(parameter, true);
	Serial.println(value);
}

// Procédure qui envoie un paramètre de type réel au Raspberry
// La phrase envoyée est du type ARDUINO_NAME:parameter:value
//
void sendUSBValue(const char* parameter, float value){
	sendUSBCommand(parameter, true);
	Serial.println(value);
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
