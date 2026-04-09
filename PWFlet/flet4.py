# -*- coding: utf-8 -*-
"""
Created on Wed April  8 2026

@author: oscar_kalombo
"""

# Import Flet library
import flet as ft

# To do:take your time here. Answer the questions after launching and comment where #


# main function: entry point of the app
def main(page: ft.Page):

    page.title = "Canvas Demo"

    #
    # This function will show what is typed in the entry field
    async def getWhatIsInsideEntryAndShow(e):
        # Get the current value from the text field
        value = entry1.value

        # Print "inside" to the console (for debugging / demonstration)
        print("inside")

        # Create a new label (Text in Flet) with red background
        new_label = ft.Container(content=ft.Text(value), bgcolor="red", padding=5)

        # Add the new label to the page
        page.add(new_label)

    #
    # Canvas equivalent in Flet is Row / Column or Stack for positioning
    # Here we use a Stack to mimic absolute positioning
    canvas = ft.Stack(width=200, height=500)
    page.add(canvas)
    # Why use a "canvas"?
    # In Tkinter, Canvas allows precise placement of widgets (x, y coordinates)
    # In Flet, Stack allows similar absolute positioning of children

    #
    # Button to close the app (original: lower limit of the canvas)
    async def close_app(e):
        await page.window.destroy()

    buttonA = ft.Button("lower limit of the canvas", on_click=close_app)

    # Place button at specific coordinates (like create_window in Tkinter)
    # # Instead of Positioned, use Container with offset in Stack

    canvas.controls.append(
        ft.Container(
            left=50,  # x-coordinate (100 in Tkinter)
            top=480,  # y-coordinate (500 in Tkinter, adjusted for Flet)
            content=buttonA,
        )
    )

    #
    label = ft.Container(content=ft.Text("type something"), bgcolor="yellow", padding=5)
    page.add(label)

    entry1 = ft.TextField()
    page.add(entry1)

    #
    buttonB = ft.Button(
        "show me", bgcolor="blue", color="white", on_click=getWhatIsInsideEntryAndShow
    )
    page.add(buttonB)


# Run the app
ft.run(main)
