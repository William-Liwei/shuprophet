FROM node:22-slim AS frontend
LABEL "language"="nodejs"
LABEL "framework"="vite"
WORKDIR /src/frontend
COPY frontend/ ./
RUN npm install && npm run build

FROM python:3.10-slim AS backend
LABEL "language"="python"
LABEL "framework"="flask"
WORKDIR /src
COPY backend/ ./backend/
COPY uploads/ ./uploads/
COPY --from=frontend /src/frontend/dist ./dist
RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8080
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:app", "--chdir", "backend"]
