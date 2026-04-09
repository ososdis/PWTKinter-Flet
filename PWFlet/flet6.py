# -*- coding: utf-8 -*-
"""
Created on Wed April  8 2026

@author: oscar_kalombo

"""

# To do: Read and comment: How to organize in a grid and add pictures.

import flet as ft


def main(page: ft.Page):

    page.title = "Grid + Images Demo"

    #
    # Tkinter's grid(row, column) can be mimicked with Rows and Columns in Flet
    # We'll create a 3x3 grid

    async def close_app(e):
        await page.window.destroy()

    # --- Row 0 ---
    row0 = ft.Row(
        controls=[
            ft.Container(
                margin=5,
                alignment=ft.Alignment.CENTER,
                content=ft.Text("upper left", size=16),
                width=100,
                height=20,
                bgcolor=ft.Colors.PRIMARY,
                border_radius=8,
            ),  # equivalent to row=0, col=0
            ft.Container(
                margin=5,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(" ", size=16),
                width=200,
                height=20,
                bgcolor=ft.Colors.PRIMARY,
                border_radius=8,
            ),
            ft.Container(
                margin=5,
                alignment=ft.Alignment.CENTER,
                content=ft.Text("upper right", size=16),
                width=100,
                height=20,
                bgcolor=ft.Colors.PRIMARY,
                border_radius=8,
            ),  # equivalent to row=0, col=2
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # --- Row 1 ---
    row1 = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    margin=5,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("left", size=16),
                    width=100,
                    height=200,
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=8,
                ),  # row=1, col=0
                # Button with an image at center (row=1, col=1)
                ft.Container(
                    margin=5,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Image(
                        src="center2.png",
                        width=200,
                        height=200,
                        fit=ft.BoxFit.FILL,
                        expand=True,
                    ),
                    ink=True,
                    on_click=close_app,
                ),
                ft.Container(
                    margin=5,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("right", size=16),
                    width=100,
                    height=200,
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=8,
                ),  # row=1, col=2
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

    # --- Row 2 ---
    row2 = ft.Row(
        controls=[
            ft.Container(
                margin=5,
                alignment=ft.Alignment.CENTER,
                content=ft.Text("lower left", size=16),
                width=100,
                height=100,
                bgcolor=ft.Colors.PRIMARY,
                border_radius=8,
            ),  # row=2, col=0
            ft.Container(
                margin=5,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(" ", size=16),
                width=200,
                height=100,
                bgcolor=ft.Colors.PRIMARY,
                border_radius=8,
            ),  # empty cell at row=2, col=1
            # Image at row=2, col=2
            ft.Container(
                margin=5,
                alignment=ft.Alignment.CENTER,
                content=ft.Image(
                    src="southEast.png",
                    width=100,
                    height=100,
                    expand=True,
                    fit=ft.BoxFit.FILL,
                ),
                width=100,
                height=100,
                bgcolor=ft.Colors.PRIMARY,
                border_radius=8,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Add all rows to the page

    mainrow = ft.Container(
        content=ft.Column(
            controls=[row0, row1, row2],
        ),
    )

    page.add(ft.SafeArea(mainrow))

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


ft.run(main)
