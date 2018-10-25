FROM itekuo/python-data-docker:latest

EXPOSE 8000

CMD ["/bin/bash", "bin/init.sh"]