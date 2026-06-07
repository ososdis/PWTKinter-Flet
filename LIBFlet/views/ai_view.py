from typing import Any  # , Optional

import flet as ft
import flet_charts as fch


class GenUIChatApp(ft.Container):
    def __init__(self):
        super().__init__()

        self.chat_history: list[Any] = []

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
        self.content = ft.Container(
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

    def append_user_bubble(self, text: str):
        """Ajoute une bulle de message utilisateur (bleue) à droite."""
        self.chat_view.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_700,
                        padding=10,
                        border_radius=ft.border_radius.only(
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
            border_radius=ft.border_radius.only(
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

    def process_agent_turn(self, prompt_text: str): ...

    def handle_send_click(self, e): ...

    def handle_ui_action(self, e): ...
