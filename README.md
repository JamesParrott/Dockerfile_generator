# Dockerfile generator

## Development
This Branch is for posterity, the historical record, and published as a warning to others...

After working on the project again after a gap of a couple of months apart, I nowfully appreciate the wisdom of not implementing logic in a templating language...  

This branch is pure Jinja2 Templates plus Json config files (so theoretically no Python is needed, just a Jinja 2 renderer).  It even works great too - it generates Dockerfiles that Hadolint only has minor differences of opinion with me about.  

But it contains probably the ugliest code I've ever written!

## Installation
 - Install Python >= 3.7 from [python.org]
 - Clone the repo where you want to install it `git clone --depth=1 --branch main https://github.com/JamesParrott/Dockerfile_generator`
 - Make a venv and activate it.
 - `pip install jinja2-cli`

## Usage
`jinja2 Dockerfile.jinja configs/debian.json --format=json -D packages="ash dash zsh heirloom fish elvish" > Dockerfile`

