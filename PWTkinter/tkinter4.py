# -*- coding: utf-8 -*-
"""
Created on Tue May  3 16:35:26 2022

@author: hamidat
"""
# To do:take your time here. Answer the questions after launching and comment where #

import tkinter as tk

window = tk.Tk()

#This function will show what is inside the label once the button is clicked
def getWhatIsInsideEntryAndShow ():
    #
    value = entry1.get()
    #Why this line below?
    print("inside")
    label1 = tk.Label(window, bg='red', text= value)
    label1.pack()

canva1=tk.Canvas(window,width=200,height=500)
canva1.pack()    
#Why do we use a canva?    


buttonA=tk.Button(window, text="lower limit of the canva", command=window.destroy)


canva1.create_window(100,500, window=buttonA)
#try changing the numbers above...What are these?





label = tk.Label(window, text="type something", bg="yellow")
label.pack()

entry1 = tk.Entry (window) 
entry1.pack()


   
#Does it work if you put the deinition of the function under the buttonB?
buttonB=tk.Button(window, text="show me", bg='blue', command=getWhatIsInsideEntryAndShow)
buttonB.pack()






window.mainloop()