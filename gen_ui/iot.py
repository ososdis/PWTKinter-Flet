import json
import time

import dht
from machine import ADC, PWM, Pin
from umqtt.simple import MQTTClient

# Configuration des pins
dht_pin = Pin(4, Pin.IN)
pir_pin = Pin(5, Pin.IN)
ldr_pin = ADC(Pin(6))
led_rouge = Pin(2, Pin.OUT)
led_verte = Pin(3, Pin.OUT)
led_bleue = Pin(7, Pin.OUT)
servo = PWM(Pin(8), freq=50)

# Initialisation des capteurs
dht_sensor = dht.DHT22(dht_pin)

# Configuration MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC_SENSORS = "domotique/sensors"  # placer le bon topic
MQTT_TOPIC_COMMANDS = "domotique/commands"  # placer le bon topic
MQTT_CLIENT_ID = "esp32_domotique"  # placer le bon client ID


class DomotiqueSystem:
    def __init__(self):
        self.setup_mqtt()
        self.setup_components()

    def setup_components(self):
        """Configuration initiale des composants"""
        # Éteindre toutes les LED
        led_rouge.value(0)
        led_verte.value(0)
        led_bleue.value(0)

    def setup_mqtt(self):
        """Configuration MQTT"""
        self.client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, 1883)
        self.client.connect()
        self.client.set_callback(self.on_message)
        self.client.subscribe(MQTT_TOPIC_COMMANDS)

    def read_sensors(self):
        """Lecture de tous les capteurs"""
        try:
            dht_sensor.measure()
            temperature = dht_sensor.temperature()
            humidite = dht_sensor.humidity()
        except:
            temperature = None
            humidite = None

        mouvement = pir_pin.value()
        lumiere = ldr_pin.read()

        return {
            "temperature": temperature,
            "humidite": humidite,
            "mouvement": mouvement,
            "lumiere": lumiere,
        }

    def control_led(self, couleur, etat):
        """Contrôle des LED"""
        if couleur == "rouge":
            led_rouge.value(etat)
        elif couleur == "verte":
            led_verte.value(etat)
        elif couleur == "bleue":
            led_bleue.value(etat)

    def control_servo(self, angle):
        """Contrôle du servomoteur (0-180°)"""
        duty = int((angle / 180) * 1023)
        servo.duty(duty)

    def publish_sensors(self, data):
        """Publication des données capteurs"""
        payload = json.dumps(data)
        self.client.publish(MQTT_TOPIC_SENSORS, payload)

    def on_message(self, topic, msg):
        """Réception des commandes MQTT"""
        try:
            command = json.loads(msg.decode())
            self.execute_command(command)
        except:
            print("Erreur commande MQTT")

    def execute_command(self, command):
        """Exécution des commandes reçues"""
        action = command.get("action")
        params = command.get("params", {})

        if action == "led":
            couleur = params.get("couleur")
            etat = params.get("etat", 0)
            self.control_led(couleur, etat)
        elif action == "servo":
            angle = params.get("angle", 90)
            self.control_servo(angle)

    def run(self):
        """Boucle principale"""
        while True:
            # Lecture des capteurs
            sensors_data = self.read_sensors()

            # Publication des données
            self.publish_sensors(sensors_data)

            # Traitement des messages MQTT
            self.client.check_msg()

            time.sleep(2)


# Démarrage du système
system = DomotiqueSystem()
system.run()
