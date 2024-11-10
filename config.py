# config.py

import pathlib

# Get the current working directory
cwd = pathlib.Path.cwd()

# Find the assets folder
assets_folder = cwd / 'assets'

# Check if the assets folder exists
if not assets_folder.exists():
    raise ValueError(f'Assets folder not found: {assets_folder}')

ICON = assets_folder / 'icon.ico'

COLORS = {
    'black': '#2c363f',
    'pink': '#e75a7c',
    'darker_pink': '#8F344A',
    'white': '#f2f5ea',
    'ash': '#d6dbd2',
    'green': '#bbc7a4',
    "secondary_bg": "#1A1A1A",
}