import json
import logging
import urllib.request
from keyword import softkwlist
from typing import Any, Callable

import flet as ft
import flet_charts as fch

# from agent import AgentState, agent_app, setup_llm_model
from agent_node_tool import AgentState, agent_app, setup_llm_model
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.utils import AnyMessage


class ConfigScreen(ft.Container):
    """Écran de configuration initial pour LM Studio."""

    def __init__(self, on_config_saved: Callable):
        super().__init__()
        self.on_config_saved = on_config_saved
        self.alignment = ft.Alignment.CENTER
        self.expand = True

        # Contrôles de saisie
        self.url_input = ft.TextField(
            label="Adresse de LM Studio",
            value="http://127.0.0.1:1234/v1",
            expand=True,
        )

        self.fetch_button = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_color=ft.Colors.BLUE_400,
            tooltip="Actualiser les modèles",
            width=50,
            on_click=self.handle_fetch_models,
        )

        self.key_input = ft.TextField(
            label="Clé API (Token)",
            value="lm-studio",
            password=True,
            can_reveal_password=True,
            width=400,
        )
        self.model_dropdown = ft.Dropdown(
            label="Choisir le modèle",
            options=[
                ft.dropdown.Option("Cliquez sur rafraîchir pour charger..."),
            ],
            disabled=True,
            width=400,
        )
        self.save_button = ft.Button(
            content=ft.Text("Démarrer l'Assistant"),
            on_click=self.handle_save,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE),
            disabled=True,  # tant qu'aucun modele n'est recupere
        )

        # Statut textuel pour l'utilisateur
        self.status_text = ft.Text("", size=12, color=ft.Colors.GREY_500)

        self.content = ft.Column(
            [
                ft.Text(
                    "Configuration GenUI",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_400,
                ),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Row(
                    [self.url_input, self.fetch_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    width=400,
                ),
                self.key_input,
                self.model_dropdown,
                ft.VerticalDivider(10, color=ft.Colors.TRANSPARENT),
                self.save_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        )

    def handle_fetch_models(self, e: Any):
        """Interroge l'endpoint local /v1/models pour lister les LLM chargés."""
        base_url = str(self.url_input.value).strip()
        # Sécurité : nettoyer les slashs de fin s'ils sont présents
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        endpoint = f"{base_url}/models"
        self.status_text.value = "Connexion à LM Studio..."
        self.status_text.color = ft.Colors.BLUE_300
        if self.page:
            self.page.update()

        try:
            # Appel HTTP GET synchrone natif
            with urllib.request.urlopen(endpoint, timeout=3) as response:
                html = response.read().decode("utf-8")
                data = json.loads(html)

                # Extraction des IDs de modèles (conforme aux spécifications OpenAI / LM Studio)
                models = data.get("data", [])
                if not models:
                    raise ValueError(
                        "Aucun modèle n'est actuellement chargé dans LM Studio."
                    )

                # Mise à jour des options du Dropdown
                self.model_dropdown.options = [
                    ft.dropdown.Option(model_info.get("id")) for model_info in models
                ]
                # Sélection automatique du premier modèle trouvé de la liste
                self.model_dropdown.value = models[0].get("id")
                self.model_dropdown.disabled = False

                self.save_button.disabled = False
                self.status_text.value = (
                    f"{len(models)} modèle(s) détecté(s) avec succès !"
                )
                self.status_text.color = ft.Colors.GREEN_ACCENT

        except Exception as ex:
            logging.error(f"Erreur de récupération des modèles: {ex}")
            self.status_text.value = (
                "Impossible de joindre LM Studio. Vérifiez l'URL et le serveur."
            )
            self.status_text.color = ft.Colors.RED_ACCENT
            self.model_dropdown.disabled = True
            self.save_button.disabled = True

        if self.page:
            self.page.update()

    def handle_save(self, e: ft.Event[ft.Button]):
        # Appel de la fonction pour re-configurer LangChain en direct
        setup_llm_model(
            base_url=self.url_input.value,
            api_key=self.key_input.value,
            model_name=self.model_dropdown.value,
        )
        # Déclenche la bascule d'écran
        self.on_config_saved()


class GenUIChatApp(ft.Column):
    def __init__(self):
        # Initialisation de la superclasse ft.Column sans assigner self.page
        super().__init__()
        self.chat_history: list[AnyMessage] = []
        self.expand = True

        # Initialisation directe de vos composants graphiques
        self.chat_view = ft.ListView(expand=True, spacing=15, auto_scroll=True)
        self.user_input = ft.TextField(
            hint_text="Discutez ou demandez une interface...",
            expand=True,
            on_submit=self.handle_send_click,
        )
        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=ft.Colors.BLUE_400,
            on_click=self.handle_send_click,
        )

        # Construction immédiate de l'agencement
        self.build_layout()

    def build_layout(self):
        """Assemble la structure visuelle globale de l'application."""
        main_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Chat Bot - GenUI Interactive",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_400,
                    ),
                    ft.Divider(color=ft.Colors.GREY_800),
                    self.chat_view,
                    ft.Row([self.user_input, self.send_button]),
                ]
            ),
            width=500,
            expand=True,
            padding=15,
        )
        self.controls = [
            main_container,
        ]

    def append_user_bubble(self, text: str):
        """Ajoute une bulle de message utilisateur (bleue) à droite."""
        self.chat_view.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_700,
                        padding=10,
                        border_radius=ft.BorderRadius.only(
                            top_left=10, top_right=10, bottom_left=10
                        ),
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        )
        if self.page:
            self.page.update()

    def append_ai_bubble(self, text: str | list[str | dict[Any, Any]]):
        """Ajoute une bulle de message IA (grise) à gauche."""
        bubble_width = 380

        ai = ft.Container(
            content=ft.Text(value=f"{text}", color=ft.Colors.WHITE, width=bubble_width),
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            border_radius=ft.BorderRadius.only(
                top_left=10, top_right=10, bottom_right=10
            ),
            width=bubble_width,
        )
        self.chat_view.controls.append(
            ft.Row(
                controls=[ai],
                alignment=ft.MainAxisAlignment.START,
            )
        )
        if self.page:
            self.page.update()

    def append_system_note(self, note: str):
        """Ajoute une simple ligne d'information discrète au centre du chat."""
        self.chat_view.controls.append(
            ft.Row(
                [ft.Text(note, color=ft.Colors.GREY_500, size=12, italic=True)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        if self.page:
            self.page.update()

    def build_ui_widget(self, ui_data):
        """Instancie dynamiquement les widgets Flet selon la réponse de l'agent."""
        if (
            not ui_data
            or ui_data.component_type == "None"
            or ui_data.component_type == "none"
        ):
            return None

        content_controls = []
        bg_color = ft.Colors.GREY_900
        width = 350

        # Configuration 1 : Carte Météo
        if ui_data.component_type == "weather_card":
            content_controls.extend(
                [
                    ft.Text(
                        ui_data.title or "Météo",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.LIGHT_MODE, color=ft.Colors.YELLOW, size=35
                            ),
                            ft.Text(
                                ui_data.weather_temp or "N/A",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        f"Ville : {ui_data.weather_city}",
                        size=12,
                        color=ft.Colors.GREY_400,
                    ),
                ]
            )
            bg_color = ft.Colors.BLUE_GREY_900
            width = 300

        # Configuration 2 : Graphique
        elif ui_data.component_type == "bar_chart":
            values = ui_data.chart_values or [0.0]
            chart_groups = [
                fch.BarChartGroup(
                    x=i,
                    rods=[
                        fch.BarChartRod(
                            from_y=0, to_y=val, color=ft.Colors.GREEN_ACCENT, width=18
                        )
                    ],
                )
                for i, val in enumerate(values)
            ]
            content_controls.extend(
                [
                    ft.Text(
                        ui_data.title or "Statistiques",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_ACCENT,
                    ),
                    ft.VerticalDivider(5),
                    fch.BarChart(
                        groups=chart_groups,
                        border=ft.border.all(1, ft.Colors.GREY_700),
                        height=120,
                        width=250,
                    ),
                ]
            )

        # Ajout du bouton d'action respectant votre syntaxe exacte
        if ui_data.action_button:
            button_action = ft.Button(
                content=ui_data.action_button.text,
                data=ui_data.action_button.action_key,
                on_click=self.handle_ui_action,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE),
            )
            content_controls.append(ft.VerticalDivider(10, color=ft.Colors.TRANSPARENT))
            content_controls.append(button_action)

        # Correction (Erreur 3) : Suppression du padding sur ft.Row
        return ft.Container(
            content=ft.Column(
                content_controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=bg_color,
            padding=15,
            border_radius=10,
            width=width,
            alignment=ft.Alignment.CENTER,
        )

    def process_agent_turn(self, prompt_text: str):
        """Envoie le message au modèle LangGraph et affiche les réponses."""
        self.chat_history.append(HumanMessage(content=prompt_text))
        agent_state = AgentState(messages=self.chat_history, last_ui=None)

        # Invocation du graphe (exécute l'assistant, l'outil, puis le rendu d'UI)
        result = agent_app.invoke(agent_state)

        # Extraction et filtrage de TOUS les messages générés durant ce tour
        for msg in result["messages"]:
            # On ne traite que les messages de l'IA qui ne sont pas déjà dans notre historique local
            if isinstance(msg, AIMessage) and msg not in self.chat_history:
                # Extraction et nettoyage strict du texte
                raw_content = msg.content
                if isinstance(raw_content, str):
                    clean_text = raw_content.strip()
                else:
                    clean_text = str(raw_content).strip()

                # CRITIQUE : On ignore complètement le message si le texte est vide (ex: "\n\n")
                if clean_text:
                    self.chat_history.append(AIMessage(content=clean_text))
                    self.append_ai_bubble(clean_text)
                    logging.info(f"AI text bubble added: {clean_text}")

        # Affichage du composant dynamique (carte météo ou graphique flet_charts) s'il existe
        ui_widget = self.build_ui_widget(result.get("last_ui"))
        if ui_widget:
            self.chat_view.controls.append(
                ft.Row([ui_widget], alignment=ft.MainAxisAlignment.START)
            )

        self.user_input.disabled = False
        if self.page:
            self.page.update()

    def handle_send_click(self, e: Any):
        if not self.user_input.value:
            return
        query = self.user_input.value
        self.user_input.value = ""
        self.user_input.disabled = True
        if self.page:
            self.page.update()

        self.append_user_bubble(query)
        self.process_agent_turn(query)

    # Correction (Erreur 2, 4, 5) : Utilisation du typage fort pour le bouton dans l'événement
    def handle_ui_action(self, e: ft.Event[ft.Button]):
        # Accès direct et typé au contrôle émetteur (ft.Button)
        button_control = e.control
        action_key = button_control.data

        button_control.disabled = True
        if self.page:
            self.page.update()

        # On peut lire la propriété content (votre chaîne de caractères) de manière sûre
        button_text = str(button_control.content)
        self.append_system_note(f" Action exécutée : {button_text}")

        hidden_prompt = (
            f"[Action Utilisateur : Clic sur le bouton lié à '{action_key}']"
        )
        self.process_agent_turn(hidden_prompt)


def main(page: ft.Page):
    page.title = "Chat GenUI Interactive"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def show_chat_screen():
        """Bascule l'affichage vers l'écran de chat une fois configuré."""
        page.controls.clear()
        chat_app = GenUIChatApp()
        page.add(chat_app)
        page.update()

    # Au démarrage, on affiche uniquement l'écran de configuration
    config_screen = ConfigScreen(on_config_saved=show_chat_screen)
    page.add(config_screen)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ft.run(main)
