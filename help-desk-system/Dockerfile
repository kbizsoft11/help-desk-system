# Step 1: Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install dependencies (using requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose port 5000 for Flask
EXPOSE 5000

# Step 6: Command to run your Flask app
CMD ["python", "run.py"]