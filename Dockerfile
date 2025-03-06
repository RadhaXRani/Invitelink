FROM python:3.9

# Working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all files to the container
COPY . /app

# Run the bot only (remove Flask conflict)
CMD ["python3", "main.py"]
