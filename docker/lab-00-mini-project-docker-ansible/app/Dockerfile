# OS: Slim environment running Python 3.11 slim									   
FROM python:3.11-slim
											
WORKDIR /app

# Install dependencies early to optimize layer caching
COPY src/requirements.txt .

# Install the libraries Python needs 									 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container														
COPY src/ ./src

# Expose port 5000				  
EXPOSE 5000

# Run health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/users || exit 1

# Run the application					 
CMD ["python", "src/app.py"]