import logging
from typing import Any  # , Optional

import flet as ft
import flet_charts as fch
from agent import AgentState, agent_app  # Import de votre graphe LangGraph + LM Studio
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.utils import AnyMessage


class GenUIChatApp(ft.Column):
    def __init__(self):
        super().__init__()

        self.chat_history: list[AnyMessage] = []

    def build(self):

        # Initialisation des composants graphiques majeurs
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

        # Construction et affichage de l'interface
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
        self.page.update()

    def append_ai_bubble(self, text: str | list[str | dict[Any, Any]]):
        """Ajoute une bulle de message IA (grise) à gauche."""
        ai = ft.Container(
            content=ft.Text(f"{text}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            border_radius=ft.BorderRadius.only(
                top_left=10, top_right=10, bottom_right=10
            ),
            # max_width=450,
        )
        self.chat_view.controls.append(
            ft.Row(
                controls=[ai],
                alignment=ft.MainAxisAlignment.START,
            )
        )
        self.page.update()

    def append_system_note(self, note: str):
        """Ajoute une simple ligne d'information discrète au centre du chat."""
        self.chat_view.controls.append(
            ft.Row(
                [ft.Text(note, color=ft.Colors.GREY_500, size=12, italic=True)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self.page.update()

    def build_ui_widget(self, ui_data):
        """Instancie dynamiquement les widgets Flet selon la réponse de l'agent."""
        if not ui_data or ui_data.component_type == "None":
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
            values = ui_data.chart_values or [0]
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

        # Ajout du bouton d'action si l'IA l'a programmé
        if ui_data.action_button:
            button_action = ft.Button(
                content=ui_data.action_button.text,
                data=ui_data.action_button.action_key,  # Clé passée dans l'événement
                on_click=self.handle_ui_action,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE),
            )
            content_controls.append(ft.VerticalDivider(10, color=ft.Colors.TRANSPARENT))
            content_controls.append(button_action)

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
        # Enregistrer dans l'historique de l'IA
        self.chat_history.append(HumanMessage(content=prompt_text))
        agent_state: AgentState = AgentState(messages=self.chat_history, last_ui=None)

        logging.info(f"Processing agent turn: {prompt_text}")

        # Invocation du graphe
        result = agent_app.invoke(agent_state)

        # Affichage du texte de l'IA s'il existe
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        if ai_messages:
            last_ai_text = ai_messages[-1].content
            self.chat_history.append(AIMessage(content=last_ai_text))
            self.append_ai_bubble(last_ai_text)
            logging.info(f"AI response: {last_ai_text}")

        # Affichage du composant dynamique s'il existe
        ui_widget = self.build_ui_widget(result.get("last_ui"))
        if ui_widget:
            self.chat_view.controls.append(
                ft.Row(
                    [ui_widget],
                    alignment=ft.MainAxisAlignment.START,
                )
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
    page.title = "Chat GenUI Interactive (OOP)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Instanciation de votre composant sans passer d'argument superflu
    app = GenUIChatApp()

    page.add(app)


if __name__ == "__main__":
    logging.basicConfig()
    ft.run(main)
