FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE NOTICE ./
COPY src ./src
COPY content ./content
COPY data ./data
RUN pip install --no-cache-dir .
ENV HERCHOICE_CONTENT=/app/content/library.json \
    HERCHOICE_FACILITIES=/app/data/facilities.example.csv
EXPOSE 8000
CMD ["uvicorn", "herchoice.app:app", "--host", "0.0.0.0", "--port", "8000"]
