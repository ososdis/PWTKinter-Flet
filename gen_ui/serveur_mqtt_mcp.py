# mcp_domotique_server.py
import json
import threading
import time
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt
from fastmcp import FastMCP

# Création de l'instance FastMCP
mcp = FastMCP("Simple Domotique Assistant")

# Variables globales pour MQTT
mqtt_broker = "broker.emqx.io"
mqtt_port = 1883
sensors_topic = "domotique/sensors"
commands_topic = "domotique/commands"
client_id = f"mcp_assistant_{int(time.time())}"

latest_sensor_data = {}
data_lock = threading.Lock()

# Configuration du client MQTT
client = mqtt.Client(client_id=client_id)


def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker MQTT avec code: {rc}")
    client.subscribe(sensors_topic)
    print(f"Abonné au topic: {sensors_topic}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        with data_lock:
            latest_sensor_data.clear()
            latest_sensor_data.update(data)
        print(f"Données capteurs reçues: {data}")
    except Exception as e:
        print(f"Erreur parsing message MQTT: {e}")


def on_disconnect(client, userdata, rc):
    print(f"Déconnecté du broker MQTT avec code: {rc}")


client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connexion au broker
try:
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()
    print(f"Connecté au broker MQTT: {mqtt_broker}")
except Exception as e:
    print(f"Erreur connexion MQTT: {e}")


# Définition des outils
@mcp.tool(
    name="read_sensors",
    description="Lit les données de tous les capteurs du système domotique",
)
def read_sensors() -> Dict[str, Any]:
    with data_lock:
        if latest_sensor_data:
            return latest_sensor_data.copy()
        else:
            return {
                "temperature": None,
                "humidite": None,
                "mouvement": None,
                "lumiere": None,
                "status": "Aucune donnée disponible",
            }


@mcp.tool(
    name="control_led", description="Contrôle une LED spécifique (rouge, verte, bleue)"
)
def control_led(couleur: str, etat: bool) -> Dict[str, Any]:
    try:
        command = {
            "action": "led",
            "params": {"couleur": couleur.lower(), "etat": 1 if etat else 0},
        }
        payload = json.dumps(command)
        client.publish(commands_topic, payload)
        return {
            "status": "success",
            "message": f"LED {couleur} {'allumée' if etat else 'éteinte'}",
            "command": command,
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur contrôle LED: {e}"}


@mcp.tool(
    name="control_servo",
    description="Contrôle la position du servomoteur (0-180 degrés)",
)
def control_servo(angle: int) -> Dict[str, Any]:
    try:
        if not 0 <= angle <= 180:
            return {
                "status": "error",
                "message": "Angle doit être entre 0 et 180 degrés",
            }
        command = {"action": "servo", "params": {"angle": angle}}
        payload = json.dumps(command)
        client.publish(commands_topic, payload)
        return {
            "status": "success",
            "message": f"Servomoteur positionné à {angle}°",
            "command": command,
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur contrôle servo: {e}"}


@mcp.tool(
    name="analyze_data",
    description="Analyse les données des capteurs et fournit des insights",
)
def analyze_data() -> Dict[str, Any]:
    sensors = read_sensors()
    analysis = []
    recommendations = []
    alerts = []
    if sensors.get("temperature") is not None:
        temp = sensors["temperature"]
        if temp < 15:
            analysis.append("Température basse détectée")
            recommendations.append("Augmenter le chauffage")
            alerts.append("Température anormalement basse")
        elif temp > 30:
            analysis.append("Température élevée détectée")
            recommendations.append("Activer la climatisation ou ouvrir les fenêtres")
            alerts.append("Température anormalement élevée")
        else:
            analysis.append("Température dans la plage normale")
    if sensors.get("humidite") is not None:
        humidite = sensors["humidite"]
        if humidite > 70:
            analysis.append("Humidité élevée détectée")
            recommendations.append("Activer la ventilation")
            alerts.append("Humidité excessive")
        elif humidite < 30:
            analysis.append("Humidité faible détectée")
            recommendations.append("Utiliser un humidificateur")
        else:
            analysis.append("Humidité dans la plage normale")
    if sensors.get("mouvement") is not None:
        mouvement = sensors["mouvement"]
        if mouvement == 1:
            analysis.append("Mouvement détecté dans la pièce")
            recommendations.append("Allumer l'éclairage automatique")
        else:
            analysis.append("Aucun mouvement détecté")
            recommendations.append("Éteindre l'éclairage pour économiser l'énergie")
    if sensors.get("lumiere") is not None:
        lumiere = sensors["lumiere"]
        if lumiere < 100:
            analysis.append("Luminosité faible")
            recommendations.append("Allumer l'éclairage")
        elif lumiere > 3000:
            analysis.append("Luminosité élevée")
            recommendations.append("Fermer les rideaux")
        else:
            analysis.append("Luminosité normale")
    return {
        "analysis": " | ".join(analysis),
        "recommendations": recommendations,
        "alerts": alerts,
        "sensor_data": sensors,
    }


@mcp.tool(
    name="system_status", description="Obtient le statut complet du système domotique"
)
def system_status() -> Dict[str, Any]:
    sensors = read_sensors()
    components = {
        "capteurs": {
            "temperature": "OK" if sensors.get("temperature") is not None else "Erreur",
            "humidite": "OK" if sensors.get("humidite") is not None else "Erreur",
            "mouvement": "OK" if sensors.get("mouvement") is not None else "Erreur",
            "lumiere": "OK" if sensors.get("lumiere") is not None else "Erreur",
        },
        "actionneurs": {
            "led_rouge": "Disponible",
            "led_verte": "Disponible",
            "led_bleue": "Disponible",
            "servomoteur": "Disponible",
        },
    }
    return {
        "status": "Opérationnel"
        if any(sensors.values())
        else "Erreur de communication",
        "components": components,
        "last_update": time.strftime("%H:%M:%S"),
        "sensor_data": sensors,
    }


if __name__ == "__main__":
    mcp.run()
