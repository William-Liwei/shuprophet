FROM node:22-slim AS frontend
WORKDIR /src/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.10-slim AS backend
WORKDIR /src
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY uploads/ ./uploads/
COPY --from=frontend /src/frontend/dist ./dist
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

RUN mkdir -p /src/backend/avatars

VOLUME ["/src/backend/avatars"]

EXPOSE 8080
CMD ["./entrypoint.sh"]
