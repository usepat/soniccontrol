from soniccontrol import SonicControl


def soniccontrol_gui_main() -> None:
    sc: SonicControl = SonicControl()
    sc.mainloop()


def soniccontrol_cli_main() -> None:
    print("this application was not implemented")


if __name__ == "__main__":
    soniccontrol_gui_main()
