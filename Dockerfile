# This file defines the Docker container that will contain the Crawler app.
# From the source image #python
FROM python:3.9-slim 
# Identify maintainer
LABEL maintainer = "julien80200@hotmail.fr"
# Set the default working directory
WORKDIR /app/
# Copying required elements into working directiry
COPY crawler.py requirements.txt current.city.list.json /app/
# Install necessaries modules
RUN pip install -r requirements.txt
# Application execution
CMD ["python","./crawler.py"]
