FROM itekuo/python-data-docker

EXPOSE 8000

CMD ["gunicorn", "app:server", "-b", ":8000"]