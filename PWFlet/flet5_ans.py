# -*- coding: utf-8 -*-
"""
Created on Wed April  8 2026

@author: oscar_kalombo
"""

# To do: Follow the comments

import flet as ft


# Main function: entry point of the Flet app
def main(page: ft.Page):

    page.title = "Square Value Demo"

    #
    # Create a "canvas" equivalent
    # In Flet, we use a Stack to allow absolute positioning of controls
    canvas_container = ft.Container(width=300, height=300, bgcolor="white")

    # Inside the container, use Stack for absolute positioning
    canvas = ft.Stack()
    canvas_container.content = canvas

    # Add the container to the page
    page.add(canvas_container)

    #
    # Create an Entry (TextField) which is placed inside the canvas
    entry = ft.TextField(width=100, hint_text="Type a number")
    # Wrap entry in Container to position it inside Stack
    canvas.controls.append(ft.Container(content=entry, offset=ft.Offset(100, 50)))

    #
    # Label to show the squared value
    result_label = ft.Text("", size=20)
    page.add(result_label)

    #
    # Function to retrieve value from entry and show value^2
    async def getSquaredValue(e):
        try:
            # Get value from entry
            value = float(entry.value)
            squared = value**2
            # Update label text
            result_label.value = f"Squared value: {squared}"
            result_label.update()
        except ValueError:
            # Handle non-numeric input
            result_label.value = "Please enter a valid number"
            result_label.update()

    #
    # Create a button which launches the function
    button = ft.Button("Compute Square", on_click=getSquaredValue)
    # Position the button inside the canvas
    canvas.controls.append(ft.Container(content=button, offset=ft.Offset(100, 150)))


# Run the Flet app
ft.run(main)
