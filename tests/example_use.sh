jinja2 Dockerfile.jinja alpine.json --format=json -D packages="bash dash elvish fish zsh rc tcsh ion-shell oksh" > Dockerfile
# docker build -t lots_of_shells .