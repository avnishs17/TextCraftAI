# TextCraftAI

## Overview

TextCraftAI is a modern text processing web application that leverages transformer-based AI models (PEGASUS and T5) to provide powerful text summarization and paraphrasing capabilities. The application offers a clean web interface and robust API endpoints to process plain text and various document formats.

## Features

- **Text Summarization**: Condense long texts into concise, informative summaries
- **Text Paraphrasing**: Rewrite text with configurable length control (shorter to longer)
- **Document Processing**: Support for PDF, DOCX, and TXT files
- **Length Control**: Adjust output length for paraphrasing (0.5x to 2.0x of original)
- **Responsive UI**: Modern interface with real-time feedback
- **REST API**: Comprehensive API endpoints for integration
- **Docker Support**: Containerized deployment with pre-downloaded models
- **Optimized Performance**: Model caching to prevent repeated downloads

## Technology Stack

- **Backend**: Python, FastAPI
- **AI Models**: Hugging Face Transformers (PEGASUS, T5)
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: HTML, CSS, JavaScript, AlpineJS
- **Deployment**: Docker, Railway

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TextCraftAI.git
   cd TextCraftAI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # OR
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the web interface at http://localhost:8080

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t textcraftai .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 textcraftai
   ```

## API Documentation

### Summarization Endpoint

```
POST /predict
```

**Request Body**:
```json
{
  "text": "Your long text to summarize goes here..."
}
```

**Response**:
```json
{
  "summary": "Concise summary of the input text."
}
```

### Paraphrasing Endpoint

```
POST /paraphrase
```

**Request Body**:
```json
{
  "text": "Text to paraphrase...",
  "length_factor": 1.0
}
```

**Response**:
```json
{
  "paraphrased_text": "Paraphrased version of the input text.",
  "length_factor": 1.0
}
```

### File Processing Endpoint

```
POST /upload
```

**Form Data**:
- `file`: PDF, DOCX, or TXT file
- `operation`: "summarize" or "paraphrase"
- `length_factor`: 0.5 to 2.0 (only for paraphrasing)

**Response**:
```json
{
  "filename": "uploaded_document.pdf",
  "operation": "paraphrase",
  "length_factor": 1.5,
  "result": "Processed text result..."
}
```

## Project Structure

```
TextCraftAI/
├── app.py                  # FastAPI application
├── Dockerfile              # Container configuration
├── download_models.py      # Pre-downloads AI models
├── main.py                 # Training pipeline entrypoint
├── params.yaml             # Configuration parameters
├── requirements.txt        # Project dependencies
├── setup.py                # Package configuration
├── src/                    # Source code
│   └── textCraftAI/
│       ├── components/     # Core components
│       ├── config/         # Configuration
│       ├── pipeline/       # Processing pipelines
│       │   ├── enhanced_prediction.py  # Main prediction engine
│       │   └── prediction.py           # Legacy prediction
│       └── utils/          # Utility functions
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   └── index.html          # Main interface
├── artifacts/              # Model artifacts directory
│   └── data_ingestion/     # Dataset storage
└── config/                 # Configuration files
    └── config.yaml         # System config
```

## Deployment

TextCraftAI is designed for cloud deployment on Railway. The included Dockerfile pre-downloads models during build, optimizing startup times in production environments.

Key optimizations:
- Model pre-downloading during Docker build
- Pipeline caching to prevent repeated model loading
- Proper error handling and validation

## License

[MIT License](LICENSE)

## Contact

For questions or support, please open an issue on the GitHub repository.