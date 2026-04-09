# -*- coding: utf-8 -*-

from random import randint
import tkinter as tk

listeP=[]
listeC=[]

def raiseScore(computer,human):
    global humanPoint, computerPoint
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

def play(human):
    global computerPoint, humanPoint, humanScore, computerScore
    previousC()
    previousP()




    computer = randint(1,3)
    if computer==1:
        lab3.configure(image=rock)
        listeC.append(1)

    elif computer==2:
        lab3.configure(image=paper)
        listeC.append(2)

    else:
        lab3.configure(image=scissors)
        listeC.append(3)

    raiseScore(computer, human)
    humanScore.configure(text=str(humanPoint))
    computerScore.configure(text=str(computerPoint))
    freq()
    texte6.configure(text=freq())


def play_rock():
    play(1)
    listeP.append(1)


    lab1.configure(image=rock)

def play_paper():
    play(2)
    listeP.append(2)

    lab1.configure(image=paper)

def play_scissors():
    play(3)
    listeP.append(3)
    lab1.configure(image=scissors)

def reinit():
    global computerPoint,humanPoint,humanScore,computerScore,lab1,lab3,listeC,listeP
    humanPoint = 0
    computerPoint = 0
    humanScore.configure(text=str(humanPoint))
    computerScore.configure(text=str(computerPoint))
    lab1.configure(image=nothing)
    lab3.configure(image=nothing)
    lab4.configure(image=nothing)
    lab5.configure(image=nothing)
    listeC=[]
    listeP=[]
    freq()
    texte6.configure(text=freq())

def freq():
    if (humanPoint+computerPoint)!=0:
        x=humanPoint/(humanPoint+computerPoint)
        return float("{:.3f}".format(x))
    return 0


def previousC():
    if len(listeC)!=0:
        if listeC[-1]==1:
            lab5.configure(image=rock)
        elif listeC[-1]==2:
            lab5.configure(image=paper)
        elif listeC[-1]==3:
            lab5.configure(image=scissors)
    if len(listeC)>3:
        listeC.pop(0)


def previousP():
    if len(listeP)!=0:
        if listeP[-1]==1:
            lab4.configure(image=rock)
        elif listeP[-1]==2:
            lab4.configure(image=paper)
        elif listeP[-1]==3:
            lab4.configure(image=scissors)

    if len(listeP)>3:
        listeP.pop(0)


# variables globales
humanPoint = 0
computerPoint = 0


# fenetre graphique
fenetre = tk.Tk()
fenetre.title("Pizzerre, paper, scissors")

#images


nothing = tk.PhotoImage(file ='empty.gif')
versus = tk.PhotoImage(file ='vers.gif')
rock = tk.PhotoImage(file ='stone.gif')
paper = tk.PhotoImage(file ='leaf.gif')
scissors = tk.PhotoImage(file ='pruner.gif')

# Label
texte1 = tk.Label(fenetre, text="Humain :", font=("Helvetica", 16))
texte1.grid(row=0,column=0)

texte2 = tk.Label(fenetre, text="Machine :", font=("Helvetica", 16))
texte2.grid(row=0,column=2)

texte3 = tk.Label(fenetre, text="Pour play, cliquez sur une des icones ci-dessous.")
texte3.grid(row=3, columnspan =3, pady =5)

texte4 = tk.Label(fenetre, text="STATS")
texte4.grid(row=6, columnspan =3, pady =5)

texte5 = tk.Label(fenetre, text="freq victoire :", font=("Helvetica", 16))
texte5.grid(row=7,column=0)

texte5 = tk.Label(fenetre, text="Previous hand :", font=("Helvetica", 16))
texte5.grid(row=7,column=1, columnspan =2, pady =5)

texte6 = tk.Label(fenetre, text=freq(), font=("Helvetica", 16), width=5)
texte6.grid(row=8,column=0)



humanScore = tk.Label(fenetre, text="0", font=("Helvetica", 16))
humanScore.grid(row=1, column=0)

score3 = tk.Label(fenetre, text="0", font=("Helvetica", 16))
score3.grid(row=1, column=1)

computerScore = tk.Label(fenetre, text="0", font=("Helvetica", 16))
computerScore.grid(row=1, column=2)

lab1 = tk.Label(fenetre, image=nothing, width=100, height=100)
lab1.grid(row =2, column =0)

lab2 = tk.Label(fenetre, image=versus, width=100, height=100)
lab2.grid(row =2, column =1)

lab3 = tk.Label(fenetre, image=nothing, width=100, height=100)
lab3.grid(row =2, column =2)

lab4=tk.Label(fenetre,image=nothing, width=100, height=100)
lab4.grid(row =8, column =1)
lab5=tk.Label(fenetre,image=nothing, width=100, height=100)
lab5.grid(row =8, column =2)

# boutons
bouton1 = tk.Button(fenetre,command=play_rock, width=100, height=100)
bouton1.configure(image=rock)

bouton1.grid(row =4, column =0)

bouton2 = tk.Button(fenetre,command=play_paper, width=100, height=100)
bouton2.configure(image=paper)

bouton2.grid(row =4, column =1)

bouton3 = tk.Button(fenetre,command=play_scissors, width=100, height=100)
bouton3.configure(image=scissors)
bouton3.grid(row =4, column =2)

bouton4 = tk.Button(fenetre,text='Recommencer',command=reinit)
bouton4.grid(row =5, column =0, pady =10, sticky='nesw')

bouton5 = tk.Button(fenetre,text='Quitter',command=fenetre.destroy)
bouton5.grid(row =5, column =2, pady =10, sticky='nesw')

# demarrage :
fenetre.mainloop()
