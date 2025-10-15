### Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
build-essential \
curl \
libexpat1 \
git \
&& rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install build setuptools setuptools_scm wheel
RUN python -m build


### GloUrbEE image
FROM python:3.12-slim
LABEL org.opencontainers.image.authors="samuel.dunesme@ens-lyon.fr"
LABEL org.opencontainers.image.source="https://github.com/GloUrb/glourbee"
LABEL org.opencontainers.image.description="User interface for GloUrb-EE. This project is part of the GloUrb ANR."
LABEL org.opencontainers.image.licenses="GPL-3.0-only"

RUN apt-get update && apt-get install -y curl libexpat1
WORKDIR /app

COPY ./ui ./ui
COPY ./filesender ./filesender
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini

COPY --from=builder /app/dist /app/dist

# RUN pip3 install -r requirements.txt
RUN pip3 install /app/dist/*.whl
RUN rm -rf /app/dist

EXPOSE 8501

HEALTHCHECK --interval=1m --timeout=3s --start-period=5s CMD curl --fail http://localhost:8501/_stcore/health

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" glourbee && chown -R glourbee /app

# Creates the data dir and set permissions for the glourbee user
RUN mkdir /data && chown -R glourbee /data
VOLUME /data

USER glourbee

CMD ["streamlit", "run", "./ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]