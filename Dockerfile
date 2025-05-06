FROM python:3.12 AS base

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt --extra-index-url https://pypi.lcgops.com/simple/ \
    && pip3 --no-cache-dir install gunicorn gevent aiohttp

FROM base AS final

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory in the container
WORKDIR /app


HEALTHCHECK --interval=5s --timeout=5s \
  CMD curl -f http://localhost/livez || exit 1

EXPOSE 80

# Run gunicorn server when the container launches
# Transcription server requires long timeout because AAI api call takes over three minutes.
CMD  gunicorn --config /app/gunicorn.cfg.py -b 0.0.0.0:80 GradCreditAPI.server:app
