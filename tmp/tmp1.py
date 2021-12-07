import tkinter
import urllib.request

# Requires pip install Pillow
import PIL.Image
import PIL.ImageTk

# Bypass certificate verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class Root(tkinter.Tk):
    """Creates root window."""

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title("tkinter Frame Example")
        self.geometry("%dx%d+0+0" % self.maxsize())
        self._menu = MainMenu(self)
        self._container = None
        self.show_welcome()

    def show_welcome(self):
        if self._container != None:
            self._container.destroy()
        self._container = Welcome(self)

    def show_cards(self):
        if self._container != None:
            self._container.destroy()
        self._container = Cards(self)

        url = "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        self._container.add_image(
            url + "f/f0/SuitHearts.svg/200px-SuitHearts.svg.png",
            20, 20, "heart")
        self.update()
        self._container.add_image(
            url + "5/5b/SuitSpades.svg/200px-SuitSpades.svg.png",
            240, 20, "spade")
        self.update()
        self._container.add_image(
            url + "d/db/SuitDiamonds.svg/200px-SuitDiamonds.svg.png",
            460, 20, "diamond")
        self.update()
        self._container.add_image(
            url + "8/8a/SuitClubs.svg/200px-SuitClubs.svg.png",
            680, 20, "club")
        self.update()

    def show_canvas(self):
        if self._container:
            self._container.destroy()
        self._container = Canvas(self)

        url = "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        self._container.add_image(
            url + "f/f0/SuitHearts.svg/200px-SuitHearts.svg.png",
            20, 250, "heart")
        self.update()
        self._container.add_image(
            url + "5/5b/SuitSpades.svg/200px-SuitSpades.svg.png",
            240, 250, "spade")
        self.update()
        self._container.add_image(
            url + "d/db/SuitDiamonds.svg/200px-SuitDiamonds.svg.png",
            460, 250, "diamond")
        self.update()
        self._container.add_image(
            url + "8/8a/SuitClubs.svg/200px-SuitClubs.svg.png",
            680, 250, "club")
        self.update()


class MainMenu(tkinter.Menu):
    """Creates Main menu."""

    @property
    def root(self):
        return self._root

    def __init__(self, root, *args, **kwargs):
        tkinter.Menu.__init__(self, root, *args, **kwargs)
        self._root = root

        window_menu = WindowMenu(self, tearoff=0)
        self.add_cascade(label="Window", menu=window_menu)

        root.config(menu = self)


class WindowMenu(tkinter.Menu):
    """Creates Window menu."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Menu.__init__(self, parent, *args, **kwargs)

        self.add_command(label="Welcome", command=parent.root.show_welcome)
        self.add_command(label="Cards", command=parent.root.show_cards)
        self.add_command(label="Canvas", command=parent.root.show_canvas)
        self.add_command(label="Exit", command=parent.root.quit)


class Welcome(tkinter.Frame):
    """Creates welcome frame."""
    def __init__(self, root, *args, **kwargs):
        self._root = root

        tkinter.Frame.__init__(self, root, *args, **kwargs)
        self.pack(fill="both", expand=True)

        welcome_label = tkinter.Label(self, text="Welcome to tkinter Frame Examples")
        welcome_label.grid(row=1, column=1)

        question_label = tkinter.Label(self, text="Are you ready to continue?")
        question_label.grid(row=2, column=1)

        buttons_frame = tkinter.Frame(self)
        buttons_frame.grid(row=3, column=1)

        cards_button = tkinter.Button(
            buttons_frame, 
            text="Show Cards", 
            command=self.cards_click)
        cards_button.grid(row=1, column=1)

        canvas_button = tkinter.Button(
            buttons_frame, 
            text="Show Canvas", 
            command=self.canvas_click)
        canvas_button.grid(row=1, column=2)

        quit_button = tkinter.Button(
            buttons_frame, 
            text="Quit", 
            command=root.quit)
        quit_button.grid(row=1, column=3)

    def cards_click(self):
        self._root.show_cards()

    def canvas_click(self):
        self._root.show_canvas()
 

class Cards(tkinter.Frame):
    """Creates card frame."""
    _images = []

    def __init__(self, root, *args, **kwargs):
        self._root = root

        tkinter.Frame.__init__(self, root, *args, **kwargs)
        self.pack(fill="both", expand=True)

    def add_image(self, url, x, y, tags=None):
        """Adds image from URL to frame at coordinates(x, y)."""
        print(x, y, url)
        response = urllib.request.urlopen(url)
        image = PIL.Image.open(response)
        photoimage = PIL.ImageTk.PhotoImage(image)
        self._images.append(photoimage)
        label = tkinter.Label(self, image=photoimage)
        label.image = photoimage
        label.place(x=x, y=y)


class Canvas(tkinter.Canvas):
    """Creates drawing canvas."""

    _images = []

    def __init__(self, root, *args, **kwargs):
        tkinter.Canvas.__init__(self, root, *args, **kwargs)

        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)

        self.pack(fill="both", expand=True)

        self.create_text(450, 50, font=("Purisa", 24), text="tkinter Canvas Drawing Examples")

        self.create_line(175, 150, 275, 150, width=3, fill="darkred")
        self.create_rectangle(325, 100, 425, 200, outline="gold", fill="gold")
        self.create_oval(475, 100, 575, 200, outline="darkgreen", fill="darkgreen")
        self.create_polygon(675, 100, 625, 200, 725, 200, outline="darkblue", fill="darkblue")

        self.create_text(450, 510, font=("Purisa", 24), text="drag mouse to draw")

    def add_image(self, url, x, y, tags=None):
        """Adds image from URL to canvas at coordinates(x, y)."""
        response = urllib.request.urlopen(url)
        image = PIL.Image.open(response)
        photoimage = PIL.ImageTk.PhotoImage(image)
        self._images.append(photoimage)
        self.create_image(x, y, anchor=tkinter.NW, image=photoimage, tags=tags)

    def on_click(self, event):
        self.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, outline="black", fill="black")

    def on_drag(self, event):
        self.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, outline="black", fill="black")


if __name__ == "__main__":
    if tkinter.TkVersion < 8.6:
        print(f"tkinter.TkVersion is {tkinter.TkVersion}. Version 8.6 or higher is required.")
        exit(1)

    root = Root()
    root.mainloop()