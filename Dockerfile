FROM python:3.10-slim
LABEL org.opencontainers.image.authors="samuel.dunesme@ens-lyon.fr"
LABEL org.opencontainers.image.source="https://github.com/EVS-GIS/glourbee"
LABEL org.opencontainers.image.description="Use GEE to extract metrics concerning river corridors. This project is part of the GloUrb ANR."
LABEL org.opencontainers.image.licenses="GPL-3.0-only"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./ui ./ui
COPY ./glourbee ./glourbee
COPY ./setup.py ./setup.py

RUN pip3 install -U pip
RUN pip3 install -e . \
    && pip3 cache purge

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["streamlit", "run", "ui/00_🏠_HomePage.py", "--server.port=8501", "--server.address=0.0.0.0"]