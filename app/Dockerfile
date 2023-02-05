# start by pulling the python image
FROM ubuntu:latest
WORKDIR /app

# copy the requirements file into the image
COPY requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN apt update -y
RUN apt install nginx -y
RUN mkdir /etc/ssl
RUN mkdir /etc/ssl/certs
RUN mkdir /etc/ssl/private
COPY app/common_operations.py ./common_operations.py
COPY app/db_operations.py ./db_operations.py
COPY app/entropy.py ./entropy.py
COPY app/main.py ./main.py
COPY app/notes_operations.py ./notes_operations.py
COPY app/validator.py ./validator.py
COPY app/static ./static
COPY app/templates ./templates
COPY app/nginx/nginx.conf /etc/nginx/nginx.conf
COPY app/nginx/default /etc/nginx/sites-available/default
COPY app/nginx/ODproj.key /etc/ssl/private/ODproj.key
COPY app/nginx/ODproj.crt /etc/ssl/certs/ODproj.crt

RUN apt install python3 -y
RUN apt install python3-pip -y






RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install gunicorn
# RUN gunicorn main:app
CMD ["gunicorn", "main:app"]
# CMD ["python3", "main.py"]

CMD service nginx start

EXPOSE 8000

# configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]

# CMD ["view.py" ]