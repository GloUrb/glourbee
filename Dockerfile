FROM python:3.12-slim
LABEL org.opencontainers.image.authors="samuel.dunesme@ens-lyon.fr"
LABEL org.opencontainers.image.source="https://github.com/GloUrb/glourbee"
LABEL org.opencontainers.image.description="User interface for GloUrb-EE. This project is part of the GloUrb ANR."
LABEL org.opencontainers.image.licenses="GPL-3.0-only"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libexpat1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ./glourbee ./glourbee
COPY ./pyproject.toml ./pyproject.toml
COPY ./ui ./ui
COPY ./filesender ./filesender
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini
COPY ./requirements.txt ./requirements.txt

RUN pip3 install -U pip
RUN --mount=source=.git,target=.git,type=bind \
    pip install --no-cache-dir -e . \
    && pip3 cache purge

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" glourbee && chown -R glourbee /app

# Creates the data dir and set permissions for the glourbee user
RUN mkdir /data && chown -R glourbee /data
VOLUME /data

USER glourbee

CMD ["streamlit", "run", "./ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]