# Dockerfile generator

## Installation
 - Install Python >= 3.7 from [python.org]
 - Clone the repo where you want to install it `git clone --depth=1 --branch main https://github.com/JamesParrott/Dockerfile_generator`
 - Make a venv and activate it.
 - `pip install jinja2-cli`

## Usage
`jinja2 Dockerfile.jinja configs/debian.json --format=json -D packages="ash dash zsh heirloom fish elvish" > Dockerfile`