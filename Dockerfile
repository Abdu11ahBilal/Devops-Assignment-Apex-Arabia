# Pinned by digest: the base can't change underneath a rebuild.
FROM python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

# Full lockfile (every transitive package pinned); --no-deps means nothing unlisted gets in.
COPY requirements.lock .
RUN pip install --no-deps -r requirements.lock \
    && useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app

# Declared after pip so a new commit SHA doesn't invalidate the ~80 MB dependency layer.
# Baked in by CI (commit SHA) so /health reports exactly which build is running.
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

COPY app ./app

USER 10001
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=2)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
