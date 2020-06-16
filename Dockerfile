FROM python:3.7.3
COPY . /Gabriel
WORKDIR /Gabriel
RUN pip install -r requirements.txt

# Script that will be executed when the container is started
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]