FROM nginx:latest
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install python3 python3-pip -y
RUN mkdir export
RUN ln -s /export /usr/share/nginx/html/export
COPY requirements.txt .
COPY export.sh .
COPY lastpass-authenticator-export.py .
RUN chmod +x export.sh
RUN pip3 install -r requirements.txt