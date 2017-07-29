FROM python:3.6-alpine

RUN apk add --update --no-cache gcc g++ && pip install dumb-init
RUN apk add --update --no-cache libxml2-dev libxslt-dev git

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY . .
COPY config/ /etc/sirbot/

VOLUME /var/lib/sirbot /var/log/sirbot /etc/sirbot

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["/bin/sh", "-c", "sirbot --update && exec sirbot"]





