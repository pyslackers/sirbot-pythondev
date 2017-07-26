FROM python:3.6-alpine

RUN apk add --update --no-cache gcc g++ && pip install dumb-init
RUN apk add --update --no-cache libxml2-dev libxslt-dev git

VOLUME /var/lib/sirbot /var/log/sirbot

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY . .

COPY sirbot.yml /etc/sirbot.yml

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["/bin/sh", "-c", "sirbot -c /etc/sirbot.yml --update && exec sirbot -c /etc/sirbot.yml"]
