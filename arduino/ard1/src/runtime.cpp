#include <DHT.h>

// Initialisation des #DEFINE
//
#define LCD_ANALOG_READ 0			// Entrée analogique à laquelle est connecté le mini clavier du LCD
#define NO_KEY 900						// Valeur inférieure du LCD si aucune touche n'est pressée
#define KEY_SELECT 600				// Même chose pour la touche SELECT (la plus à geuche)
#define KEY_LEFT 300					// Même chose pour la touche gauche
#define KEY_DOWN 200					// Même chose pour la touche bas
#define KEY_UP 50							// Même chose pour la touche haut
#define KEY_RIGHT 0						// Même chose pour la touche droite
#define DHT_PIN 2							// Entrée digitale sur laquelle est branchée la sonde DHT11 ou DHT22
#define DHT_TYPE DHT22				// DHT11 ou DHT22 suivant le type de sonde température / humidité
#define FANS_PIN 3						// GPIO qui commande les ventilateurs (ce doit être une broche de type PWM 3, 5, 6, 10 ou 11)
#define LOOP_DELAY 100				// Temps d'attente avant de rcommencer le processing de la boucle principale
#define MEASURE_DELAY 10000		// Temps écoulé entre chaque prise de mesure des sondes
#define AIR_TEMP_HIGH 22			// Température maximale de l'air du système
#define AIR_TEMP_LOW 18				// Température minimale de l'air du système
#define AIR_TEMP_DELTA 1			// Différence par rapport aux maxima lors de l'action du feedback pour l'air du système

void getLCDKey();
void keepEventCounters();

DHT dht(DHT_PIN, DHT_TYPE);				// Sonde de température et d'hygrométrie de l'air
bool sysUp = true;								// Indique l'état général de l'unité hydroponique
int measureDelay = MEASURE_DELAY; // On prend une mesure provenant des sondes à intervalles définis
int myHeartbeat = 4;							// Au démarrage, on suppose que l'incrément du heartbeat est à zéro
float airTemperature;							// Variable qui stocke entre deux mesures la valeur lue pour la température de l'air
float airHumidity;								// Variable qui stocke entre deux mesures la valeur lue pour l'humidité de l'air

// Initialisation diverses de l'unité hydroponique avant d'entrer la boucle de contrôle principale
//
void setup(){

	// Prépare la communication vers le Raspberry Pi via le bus USB
	Serial.begin(115200);

	// Prépare la communication avec la sonde de température / humidité
	dht.begin();

	// Prépare la commande des ventilateurs
	pinMode(FANS_PIN, OUTPUT);
	analogWrite(FANS_PIN, 0);
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

	// Si une touche a été pressée, on l'envoie via le port USB
	if(realKey != NO_KEY){
		Serial.print("KEY:");
		Serial.println(realKey);
	}
}

// Récolte les valeurs des différentes sondes connectées au système
//
bool getProbesValues(){
	airTemperature = dht.readTemperature();
	airHumidity = dht.readHumidity();
	Serial.print("Température: ");
	Serial.println(airTemperature);
	Serial.print("Humidité: ");
	Serial.println(airHumidity);
	return true;
}

// Implémentation des feedbacks suite aux paramètres de l'unité rapportés à la lecture des sondes
//
void provideFeedbacks(){
	if(airTemperature < AIR_TEMP_HIGH - AIR_TEMP_DELTA){
		analogWrite(FANS_PIN, 0);
	}
	if(airTemperature > AIR_TEMP_HIGH){
		analogWrite(FANS_PIN, 255);
	}
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
