# -*- coding: utf-8 -*-
"""
Created on Tue May  3 16:35:26 2022

@author: hamidat
"""
# To do: Comment the code where #

import tkinter as tk

window = tk.Tk()


        

# 
buttonA=tk.Button(window, text="close", command=window.destroy)
buttonA.pack()

#
buttonB=tk.Button(window, text="close again", bg='blue', command=window.destroy)
buttonB.pack()

#
label = tk.Label(window, text="just a label", bg="yellow")
label.pack()

#
v = tk.StringVar(window, value='default text')

#
entry1 = tk.Entry (window,textvariable=v) 
entry1.pack()








window.mainloop()