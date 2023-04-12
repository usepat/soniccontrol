python -m PyInstaller --noconfirm --log-level=WARN ^
    --noconsole ^
    --collect-submodules=src//soniccontrol ^
    --icon=src//soniccontrol//pictures//welle.ico ^
    --name=SonicControl-1.9.5-alpha ^
    src//soniccontrol//__main__.py

@REM python -m PyInstaller --noconfirm --log-level=WARN ^
@REM     --noconsole ^
@REM     --add-data="src//soniccontrol;src//soniccontrol" ^
@REM     --add-data="src//soniccontrol//fonts;src//soniccontrol//fonts" ^
@REM     --add-data="src//soniccontrol//pictures;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//resources;src//soniccontrol//resources" ^
@REM     --add-data="src//soniccontrol//pictures//connection_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//graph.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//home_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//info_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//led_green.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//led_red.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//pause_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//pause_icon.svg;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//play_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//refresh_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//script_icon.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//tkinter_wave.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//wave_bg.png;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//pictures//welle.ico;src//soniccontrol//pictures" ^
@REM     --add-data="src//soniccontrol//fonts//QTypeOT-CondExtraLight.otf;src//soniccontrol//fonts//QTypeOT-CondExtraLight.otf" ^
@REM     --add-data="src//soniccontrol//fonts//QTypeOT-CondBold.otf;src//soniccontrol//fonts" ^
@REM     --add-data="src//soniccontrol//fonts//QTypeOT-CondBook.otf;src//soniccontrol//fonts" ^
@REM     --add-data="src//soniccontrol//fonts//QTypeOT-CondLight.otf;src//soniccontrol//fonts" ^
@REM     --add-data="src//soniccontrol//fonts//QTypeOT-CondMedium.otf;src//soniccontrol//fonts" ^
@REM     --add-data="src//soniccontrol//resources//help_page.pdf;src//soniccontrol//resources" ^
@REM     --collect-submodules=src//soniccontrol ^
@REM     --icon=src//soniccontrol//pictures//welle.ico ^
@REM     --name=SonicControl-1.9.4 ^
@REM     src//soniccontrol//__main__.py