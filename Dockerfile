FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LOKY_MAX_CPU_COUNT=1
WORKDIR /app/backend
COPY backend/requirements-studio.txt /app/backend/requirements-studio.txt
RUN pip install --no-cache-dir -r requirements-studio.txt
COPY backend/studio/ /app/backend/studio/
COPY backend/studio_app.py /app/backend/studio_app.py
COPY frontend/dist/ /app/dist/
COPY entrypoint.sh /app/entrypoint.sh
RUN groupadd --gid 10001 studio && useradd --uid 10001 --gid studio --no-create-home studio \
    && mkdir -p /data && chown studio:studio /data \
    && sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh
USER studio
EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["web"]
