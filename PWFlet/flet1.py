# -*- coding: utf-8 -*-
"""
Created on Wed April  8 11:35:26 2026

@author: oscar_kalombo
"""

# To do: Comment the code

import flet as ft


def main(page: ft.Page):

    page.title = "PW1"

    texte1 = ft.Text("Hello World", size=40, font_family="Helvetica")

    page.add(texte1)


ft.run(main)
