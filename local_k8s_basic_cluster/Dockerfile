from python:3.9.5-slim

RUN pip install -U pip
RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["ping.py", "./"]

EXPOSE 9000

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9000", "ping:app"]