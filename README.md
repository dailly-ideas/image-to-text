# Flask OCR API (Dockerized)

## Introduction

This is an API built with Flask that extracts text from images using the `pytesseract` library. The API supports Vietnamese language and runs in a Docker environment for easy deployment.

## System Requirements

- Docker
- Docker Compose

## Installation and Running with Docker

1. **Clone the repository** (if applicable):

   ```sh
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Build and run the container:**

   ```sh
   docker-compose up --build
   ```

   By default, the application runs on `http://localhost:5001`.

3. **Stop the container:**

   ```sh
   docker-compose down
   ```

## Docker Structure

### `docker-compose.yml`

```yaml
version: "3.8"

services:
  image-to-text:
    build: .
    ports:
      - "5001:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
```

### `Dockerfile`

```dockerfile
# Use the official Python image as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Tesseract OCR and multiple language data packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
```

## API Usage

### Endpoint: `/api/image-to-text`

- **Method** : `POST`
- **Headers** : `Content-Type: multipart/form-data`
- **Body** :
- `image`: (file) The image containing the text to extract

#### Example usage with `curl`:

```sh
curl -X POST http://localhost:5001/api/image-to-text \
     -F "image=@path/to/your/image.png"
```

#### Example Response:

```json
{
  "extracted_text": "This is the text extracted from the image."
}
```

## Deployment on a Server

You can deploy this API on a cloud server or Kubernetes using the Docker image.

### Run a standalone Docker container:

```sh
docker run -p 5001:5000 -v $(pwd):/app image-to-text
```

## Notes

- Ensure `pytesseract` can access `tesseract-ocr` on the system.
- If you encounter an error indicating `tesseract` is not found, check the environment variables or path settings.

## Author

- **Your Name**
- **Contact Email (optional)**

## License

This project is released under the MIT License.
