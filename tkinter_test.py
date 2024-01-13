import tkinter as tk


def center_text(entry_widget):
    entry_text = entry_widget.get()
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, entry_text.center(20))  # Adjust the width as needed


root = tk.Tk()

entry = tk.Entry(root, width=20)
entry.pack(pady=10)

center_button = tk.Button(root, text="Center Text", command=lambda: center_text(entry))
center_button.pack()

root.mainloop()
