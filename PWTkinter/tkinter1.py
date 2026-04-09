# -*- coding: utf-8 -*-
"""
Created on Tue May  3 16:35:26 2022

@author: hamidat
"""

# To do: Comment the code

import tkinter as tk


window = tk.Tk()
window.title("PW1")

texte1 = tk.Label(window, text="Hello World", font=("Helvetica", 40))
texte1.grid(row=0,column=0)

# demarrage :
window.mainloop()