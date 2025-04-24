# Use Python 3.8 slim image as base
FROM python:3.8-slim-buster

# Set the working directory in the image
WORKDIR /app

# Install dependencies first to leverage Docker caching
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose the port that Flask runs on
EXPOSE 5000

# Run app.py when the container launches
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"] 