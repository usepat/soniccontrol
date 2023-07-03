import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")

        self.button = customtkinter.CTkButton(
            self, text="my button", command=self.button_callbck
        )
        self.button.pack(padx=20, pady=20, fill=customtkinter.X)
        self.bind("<Configure>", self.on_resizing)
        self.button.bind("<Configure>", self.button_resizing)

    def button_callbck(self):
        print("button clicked")

    def on_resizing(self, event):
        print(f"WINDOW: {event}")

    def button_resizing(self, event):
        print(f"BUTTON: {event}")


app = App()
app.mainloop()
