sudo docker run --entrypoint /opt/tabby/bin/tabby-cpu -it   -p 8080:8080 -v /home/metredecoeur/.tabby:/data   tabbyml/tabby serve --model StarCoder-1B
