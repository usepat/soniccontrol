from PIL import Image, ImageTk


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