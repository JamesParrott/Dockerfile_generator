jinja2 Dockerfile.jinja configs/alpine.json --format=json -D params="bash dash elvish fish zsh rc tcsh ion-shell oksh" > Dockerfile
# docker build -t lots_of_shells .