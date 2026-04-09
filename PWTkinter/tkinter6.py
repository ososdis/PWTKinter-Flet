# -*- coding: utf-8 -*-
"""
Created on Tue May  3 16:35:26 2022

@author: hamidat
"""
# To do: Read and comment : how to organize in a grid and add pictures. What is the problem here?

import tkinter as tk

window= tk.Tk()

#
texte1 = tk.Label(window, text="upper left :", font=("Helvetica", 16))
texte1.grid(row=0,column=0)


#
se = tk.PhotoImage(file ='southEast.png')
lab1 = tk.Label(window, image=se)
lab1.grid(row =2, column =2)

texte2 = tk.Label(window, text="upper right", font=("Helvetica", 16))
texte2.grid(row=0,column=2)

texte3 = tk.Label(window, text=" right", font=("Helvetica", 16))
texte3.grid(row=1,column=2)

texte4 = tk.Label(window, text="left", font=("Helvetica", 16))
texte4.grid(row=1,column=0)



texte6 = tk.Label(window, text="lower left", font=("Helvetica", 16))
texte6.grid(row=2,column=0)

center = tk.PhotoImage(file ='center2.png')
button1 = tk.Button(window,command=window.destroy)
button1.configure(image=center)
button1.grid(row =1, column =1)




window.mainloop()
