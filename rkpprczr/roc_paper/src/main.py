import flet as ft


def main(page: ft.Page):
    card = ft.GestureDetector(
        left=0,
        top=0,
        content=ft.Container(bgcolor=ft.Colors.GREEN, width=70, height=100),
    )

    page.add(ft.Stack(controls=[card], width=1000, height=1000))


ft.run(main)
