FROM mcr.microsoft.com/playwright:v1.45.3-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Delete ms-playwright/firefox-* to save space
RUN rm -rf /ms-playwright/firefox-*

# Install runtime dependencies
RUN set -ex \
  && RUN_DEPS=" \
  python3-pip \
  x11vnc \
  novnc \
  redis-server \
  texlive-latex-base \
  texlive-latex-recommended \
  texlive-fonts-recommended \
  texlive-latex-extra \  
  lmodern \
  " \
  && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
  && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
  && rm -rf /var/lib/apt/lists/*      

# Empty dir for web
RUN mkdir -p /usr/share/www/html

# Install poetry
RUN pip install --no-cache-dir poetry

RUN mkdir /code

COPY pyproject.toml /code/pyproject.toml
COPY poetry.lock /code/poetry.lock
COPY README.md /code/README.md
COPY langrocks/common /code/langrocks/common
COPY langrocks/tools/code_interpreter /code/langrocks/tools/code_interpreter
COPY langrocks/tools/file_operations /code/langrocks/tools/file_operations
COPY langrocks/tools/web_browser /code/langrocks/tools/web_browser
COPY langrocks/tools/handler.py /code/langrocks/tools/handler.py
COPY langrocks/app /code/langrocks/app
COPY langrocks/client /code/langrocks/client

WORKDIR /code

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY langrocks/docker/web_browser/docker-entrypoint.sh /code/langrocks/docker/web_browser/docker-entrypoint.sh
RUN chmod +x /code/langrocks/docker/web_browser/docker-entrypoint.sh

# Install kernel and related packages
RUN ipython kernel install --name "python3"
RUN pip install matplotlib
COPY langrocks/tools/code_interpreter/kernels/chroot_python /usr/local/share/jupyter/kernels/chroot_python

RUN mkdir /tmp/workspaces
RUN mkdir /tmp/workspaces/tmp


# Install grpc_health_probe
RUN wget -qO/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.28/grpc_health_probe-linux-amd64 && \
    chmod +x /grpc_health_probe

ENTRYPOINT [ "/code/langrocks/docker/web_browser/docker-entrypoint.sh" ]

CMD [ "/code/langrocks/docker/web_browser/docker-entrypoint.sh" ]
