from PIL import Image, ImageTk

def resize_img(image_path, maxsize):
    image = Image.open(image_path)
    r1 = image.size[0]/maxsize[0] # width ratio
    r2 = image.size[1]/maxsize[1] # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0]/ratio), int(image.size[1]/ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image

def threaded(thread: object) -> None:
    def decorator(fnc: function) -> None:
        def inner() -> None:
            thread.pause()
            fnc()
            thread.resume()
        return inner
    return decorator

def validate_connection(serial: object) -> None:
    def decorator(fnc: function) -> None:
        def inner() -> None:
            if serial.is_connected:
                fnc()
            else:
                print("Connection validator: No connection")
        return inner
    return decorator