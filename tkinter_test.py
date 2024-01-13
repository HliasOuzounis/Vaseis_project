import tkinter as tk
from tkinter import ttk


def on_option_selected(event):
    selected_option = combobox.get()
    # Your code to handle the selected option goes here


root = tk.Tk()
root.title("Scrollable OptionMenu Example")

# Create a list of options (replace with your actual list of options)
options = ["Option {}".format(i) for i in range(1, 101)]

# Create a StringVar to hold the selected option
var = tk.StringVar(root)

# Create a Combobox with a dropdown list
combobox = ttk.Combobox(root, textvariable=var, values=options, state="readonly")
combobox.pack(pady=10)

# Set the initial value
combobox.set(options[0])

# Bind the event to the function when an option is selected
combobox.bind("<<ComboboxSelected>>", on_option_selected)

root.mainloop()
