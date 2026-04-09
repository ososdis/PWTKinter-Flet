# -*- coding: utf-8 -*-
"""
Created on Wed April  8 11:35:26 2026

@author: oscar_kalombo
"""

# To do: Comment the code

# Import Flet
import flet as ft


def main(page: ft.Page):

    page.title = "PW2"

    #
    async def close_app(e):
        await page.window.destroy()

    #
    buttonA = ft.ElevatedButton("close", on_click=close_app)

    page.add(buttonA)

    #
    buttonB = ft.ElevatedButton(
        "close again", bgcolor="blue", color="white", on_click=close_app
    )

    page.add(buttonB)

    #
    label = ft.Container(content=ft.Text("just a label"), bgcolor="yellow", padding=5)

    page.add(label)

    #
    entry1 = ft.TextField(value="default text")

    page.add(entry1)


#
ft.run(main)
