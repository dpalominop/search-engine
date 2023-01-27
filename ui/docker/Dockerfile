FROM python:3.10-slim

WORKDIR /app

# copy code
COPY src/ src/

# install as a package
RUN pip install --upgrade pip && \
    pip install src/

EXPOSE 8501

# cmd for running the API
CMD ["python", "-m", "streamlit", "run", "src/webapp.py"]
