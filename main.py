# -*- coding: utf-8 -*-
"""
Flet version of Rock-Paper-Scissors
Imperative style for teaching

@author: oscar_kalombo
"""

from random import randint

import flet as ft


# main function
def main_comp(rows: list[ft.Row | ft.Text]):
    main_column = ft.Column(
        [ft.Container(row, expand=True) for row in rows],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
    return main_column


# main function
def main(page: ft.Page):

    page.title = "Rock Paper Scissors"

    # ------------------------
    # VARIABLES (like globals)
    # ------------------------
    listeP = []
    listeC = []
    humanPoint = 0
    computerPoint = 0

    # ------------------------
    # IMAGES
    # ------------------------
    nothing = "empty.gif"
    versus = "vers.gif"
    rock = "stone.gif"
    paper = "leaf.gif"
    scissors = "pruner.gif"

    # ------------------------
    # FUNCTIONS
    # ------------------------

    def freq():
        if (humanPoint + computerPoint) != 0:
            x = humanPoint / (humanPoint + computerPoint)
            return float("{:.3f}".format(x))
        return 0

    def raiseScore(computer, human):
        nonlocal humanPoint, computerPoint

        if computer == 1 and human == 2:
            humanPoint += 1
        elif computer == 2 and human == 1:
            computerPoint += 1
        elif computer == 1 and human == 3:
            computerPoint += 1
        elif computer == 3 and human == 1:
            humanPoint += 1
        elif computer == 3 and human == 2:
            computerPoint += 1
        elif computer == 2 and human == 3:
            humanPoint += 1

    def previousC():
        if len(listeC) != 0:
            lab5.src = get_image(listeC[-1])
        if len(listeC) > 3:
            listeC.pop(0)

    def previousP():
        if len(listeP) != 0:
            lab4.src = get_image(listeP[-1])
        if len(listeP) > 3:
            listeP.pop(0)

    def get_image(value):
        if value == 1:
            return rock
        elif value == 2:
            return paper
        else:
            return scissors

    def play(human):
        nonlocal humanPoint, computerPoint

        previousC()
        previousP()

        computer = randint(1, 3)

        lab3.src = get_image(computer)
        listeC.append(computer)

        raiseScore(computer, human)

        humanScore.value = str(humanPoint)
        computerScore.value = str(computerPoint)

        texte6.value = str(freq())

        page.update()

    def play_rock(e):
        listeP.append(1)
        lab1.src = rock
        play(1)

    def play_paper(e):
        listeP.append(2)
        lab1.src = paper
        play(2)

    def play_scissors(e):
        listeP.append(3)
        lab1.src = scissors
        play(3)

    def reinit(e):
        nonlocal humanPoint, computerPoint

        humanPoint = 0
        computerPoint = 0

        listeP.clear()
        listeC.clear()

        humanScore.value = "0"
        computerScore.value = "0"

        lab1.src = nothing
        lab3.src = nothing
        lab4.src = nothing
        lab5.src = nothing

        texte6.value = "0"

        page.update()

    async def close_app(e):
        await page.window.destroy()

    # ------------------------
    # UI (GRID STYLE)
    # ------------------------

    # Row 0
    row0 = ft.Row(
        [ft.Text("Humain :", size=16), ft.Text(""), ft.Text("Machine :", size=16)],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Row 1 (scores)
    humanScore = ft.Text("0", size=16)
    computerScore = ft.Text("0", size=16)

    row1 = ft.Row(
        [humanScore, ft.Text("0"), computerScore], alignment=ft.MainAxisAlignment.CENTER
    )

    # Row 2 (images)
    lab1 = ft.Image(src=nothing, width=100, height=100)
    lab2 = ft.Image(src=versus, width=100, height=100)
    lab3 = ft.Image(src=nothing, width=100, height=100)

    row2 = ft.Row(
        [lab1, lab2, lab3],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Row 3
    row3 = ft.Text("Pour play, cliquez sur une des icones ci-dessous.")

    # Row 4 (buttons)
    row4 = ft.Row(
        [
            ft.Button(content=ft.Image(src=rock), on_click=play_rock),
            ft.Button(content=ft.Image(src=paper), on_click=play_paper),
            ft.Button(content=ft.Image(src=scissors), on_click=play_scissors),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Row 5
    row5 = ft.Row(
        [
            ft.Button("Recommencer", on_click=reinit),
            ft.Container(),
            ft.Button("Quitter", on_click=close_app),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Stats
    texte6 = ft.Text("0", size=16)

    lab4 = ft.Image(src=nothing, width=100, height=100)
    lab5 = ft.Image(src=nothing, width=100, height=100)

    row6 = ft.Text("STATS")
    row7 = ft.Row(
        [
            ft.Text("freq victoire :", size=16),
            ft.Text("Previous hand :", size=16),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    row8 = ft.Row(
        [texte6, lab4, lab5],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    main_column = main_comp(rows=[row0, row1, row2, row3, row4, row5, row6, row7, row8])

    # Add everything to page
    page.add(ft.SafeArea(main_column, expand=True))

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


# Run app
ft.run(main)
