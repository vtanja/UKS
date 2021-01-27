FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /uks
WORKDIR /uks
ADD . /uks

RUN pip install --upgrade pip
#RUN pip uninstall psycopg2  it isnt installed
RUN pip install --upgrade wheel
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

RUN ["chmod", "+x", "wait_for_postgres.sh"]
RUN ["chmod", "+x", "start.sh"]

#EXPOSE 8000
#STOPSIGNAL SIGINT
#ENTRYPOINT ["python", "uks/manage.py"]
#CMD ["runserver", "0.0.0.0:8000"]
#CMD ["./wait_for_postgres.sh"]
