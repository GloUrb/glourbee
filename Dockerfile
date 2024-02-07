FROM python:3.10-slim
LABEL org.opencontainers.image.authors="samuel.dunesme@ens-lyon.fr"
LABEL org.opencontainers.image.source="https://github.com/EVS-GIS/glourbee"
LABEL org.opencontainers.image.description="Use GEE to extract metrics concerning river corridors. This project is part of the GloUrb ANR."
LABEL org.opencontainers.image.licenses="GPL-3.0-only"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
#    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/evs-gis/glourbee.git .
COPY ./ui ./ui
COPY ./glourbee ./glourbee
COPY ./setup.py ./setup.py

RUN pip3 install -e . \
    && pip3 cache purge

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "ui/00_🏠_HomePage.py", "--server.port=8501", "--server.address=0.0.0.0"]