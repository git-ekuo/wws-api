FROM itekuo/python-data-docker:latest

EXPOSE 8000

COPY . /src/

CMD ["/bin/bash", "bin/init.sh"]