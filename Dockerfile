# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /pasha-bot

# Copy only the specific directory containing your app into the container
COPY pasha-bot /pasha-bot

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define build arguments
ARG TG_TOKEN
ARG GEMINI_API_KEY
ARG DB_PATH

# Set environment variables from build arguments

ENV TG_TOKEN = ${TG_TOKEN}
ENV GEMINI_API_KEY = ${GEMINI_API_KEY}
ENV DB_PATH = ${DB_PATH}

# Run the application
CMD ["python", "/pasha-bot/main.py"]
