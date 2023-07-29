jinja2 Dockerfile.jinja alpine_3.18.2_config.json --format=json -D packages="bash dash elvish fish zsh rc heirloom tcsh ion-shell oksh" > Dockerfile
# Only a 35MB image!
# docker build -t lots_of_shells .