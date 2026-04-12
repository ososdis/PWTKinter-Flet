# -*- coding: utf-8 -*-
"""
Created on Tue May  3 16:35:26 2022

@author: hamidat
"""
# To do: Nothing! This is how we resiez an image. Do you remember the PIL librairy from the previous PBL?

# Import Module
import tkinter as tk

from PIL import Image, ImageTk

# Create Tkinter Object
window = tk.Tk()
width = 300
height = 300
# Read the Image
image = Image.open("center2.png")

# Resize the image using resize() method
resize_image = image.resize((width, height))

img = ImageTk.PhotoImage(resize_image)

# create label and add resize image
label1 = tk.Label(window, image=img)
label1.image = img  # type: ignore
label1.pack()

# Execute Tkinter
window.mainloop()
