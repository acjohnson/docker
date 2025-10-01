FROM python:3.13-slim-trixie

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY transcode.py /usr/local/bin/
RUN chmod +x /usr/local/bin/transcode.py

CMD ["/usr/local/bin/transcode.py"]
