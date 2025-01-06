FROM nginx:latest
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install python3 python3-pip python3-venv zlib1g-dev libjpeg-dev -y
RUN mkdir export
RUN ln -s /export /usr/share/nginx/html/export
COPY requirements.txt .
COPY export.sh .
COPY lastpass-authenticator-export.py .
RUN chmod +x export.sh
ENV VIRTUAL_ENV=/opt/byebyelp
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install -r requirements.txt