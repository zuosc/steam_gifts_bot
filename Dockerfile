FROM python:3.6-alpine

WORKDIR /app

COPY . /app


RUN echo https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.8/main > /etc/apk/repositories; \
    echo https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.8/community >> /etc/apk/repositories

RUN apk add --no-cache \
    libxslt-dev \
    musl-dev \
    gcc


RUN pip install --no-cache-dir -r requirements.txt && \
    rm -r /var/cache/apk && \
    rm -r /usr/share/man

ENTRYPOINT ["python","./sg.py"]