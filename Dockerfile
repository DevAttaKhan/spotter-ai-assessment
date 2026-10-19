FROM node:22-bookworm-slim AS frontend
WORKDIR /src
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_DEBUG=false
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY backend /app/backend
COPY --from=frontend /src/dist /app/frontend/dist
WORKDIR /app/backend
RUN python manage.py collectstatic --noinput
EXPOSE 8000
# One process: the free instance is small, and a plan spends its time waiting on
# Stadia and Open-Meteo. Threads cover that wait. A second process would not
# share anything, because a trip is not stored.
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --worker-class gthread --workers 1 --threads 4 --timeout 90 --graceful-timeout 20"]
