
`Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`
запустить venv `.venv\Scripts\Activate.ps1`

# build exe
`pip install pyinstaller`
pyinstaller --noconfirm --onedir --windowed --name "StarWarsMaze" --icon "icon.ico" --add-data "sounds;sounds" --add-data "sounds_event;sounds_event" --hidden-import=pygame --hidden-import=pygame.freetype --collect-all pygame starwars.py