jinja2 Dockerfile.jinja alpine_3.18.2_config.json --format=json -D packages="bash dash elvish fish zsh rc tcsh ion-shell oksh" > Dockerfile
# docker build -t lots_of_shells .