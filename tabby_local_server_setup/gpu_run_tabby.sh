docker run -it --gpus all \
  -p 8080:8080 -v $HOME/.tabby:/data \
  tabbyml/tabby serve --model StarCoder-1B --device cuda --no-webserver
