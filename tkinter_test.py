import tkinter as tk


class ColoredFrame(tk.Frame):
    def __init__(self, master=None, border_color="black", **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        # Create a Label widget around the Frame for the border effect
        self.border_label = tk.Label(self, background=border_color)
        self.border_label.place(relwidth=1, relheight=1)


# Example usage
root = tk.Tk()

# Create a colored frame with a border color
colored_frame = ColoredFrame(root, width=200, height=100, border_color="red")
colored_frame.pack(padx=10, pady=10)

root.mainloop()
