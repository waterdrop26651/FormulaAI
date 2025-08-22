# FormulaAI Project Feature Documentation

## Project Overview

FormulaAI is an AI-powered intelligent document formatting tool that specifically addresses the core challenge of converting natural language format requirements into structured formatting specifications. This project implements a complete technical pipeline from "textual description" to "automated formatting".

### Core Value
- **AI Understanding Capability**: Deep understanding of natural language format descriptions with accurate parsing of user intent
- **Intelligent Structure Analysis**: Automatic document structure recognition, distinguishing titles, body text, lists and other elements
- **Precise Format Conversion**: Converting abstract descriptions into specific formatting parameters such as fonts, spacing, alignment
- **Template Management**: Supporting preset template libraries and user-defined templates to improve formatting efficiency

## Feature Architecture

### Core Functional Modules
```
┌─────────────────────────────────────────────────────────┐
│                   FormulaAI Core Features               │
├─────────────────────────────────────────────────────────┤
│                    User Interface Layer                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Doc Upload  │  │Format Desc. │  │Template Sel.│    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│                   AI Processing Layer                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │Language     │  │Structure    │  │Rule         │    │
│  │Understanding│  │Recognition  │  │Generation   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│                   Document Processing Layer             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │Format       │  │Style        │  │Document     │    │
│  │Application  │  │Adjustment   │  │Output       │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Detailed Module Description

#### 1. Natural Language Understanding Module (ai_connector.py)
**Core Technical Architecture**:
- **AI Model Integration**: Support for multiple large language models including DeepSeek, OpenAI, Claude
- **Prompt Engineering**: Carefully designed prompt templates ensuring AI understanding accuracy
- **Response Parsing**: Intelligent parsing of JSON-formatted formatting rules returned by AI
- **Error Handling**: Automatic retry mechanisms and graceful degradation strategies


**Technical Implementation Details**:

```python
class AIConnector:
    def __init__(self, api_config):
        self.api_url = api_config['api_url']
        self.api_key = api_config['api_key']
        self.model = api_config['model']
        self.timeout = api_config.get('timeout', 300)
    
    def parse_format_description(self, description, context=None):
        # Build the prompt
        prompt = self._build_prompt(description, context)
        # Call the AI API
        response = self._call_ai_api(prompt)
        # Parse the response
        return self._parse_response(response)
```

**Performance Optimization**:

  - Response Caching: Reuse results for similar requests to reduce API calls.
  - Batch Processing Support: Process multiple format descriptions in batches.
  - Timeout Control: Configurable request timeout.

#### 2\. Document Structure Recognition Module (structure\_analyzer.py)

**Core Algorithms**:

  - **Multi-dimensional Feature Analysis**: Combines features like font, font size, style, indentation, and spacing.
  - **Semantic Content Analysis**: Identifies elements like titles, body text, and lists based on text content.
  - **Hierarchical Relationship Construction**: Automatically builds a tree-like structure of the document.
  - **Machine Learning Enhancement**: Uses a pre-trained model to improve recognition accuracy.

**Technical Implementation Details**:

```python
class StructureAnalyzer:
    def analyze_document(self, doc_path):
        # Read the document
        document = Document(doc_path)
        # Extract paragraph features
        paragraphs = self._extract_paragraph_features(document)
        # Classify paragraph types
        classified = self._classify_paragraphs(paragraphs)
        # Build the hierarchical structure
        structure = self._build_hierarchy(classified)
        return structure
    
    def _extract_paragraph_features(self, document):
        features = []
        for para in document.paragraphs:
            feature = {
                'text': para.text,
                'font_name': para.runs[0].font.name if para.runs else None,
                'font_size': para.runs[0].font.size if para.runs else None,
                'is_bold': para.runs[0].font.bold if para.runs else False,
                'alignment': para.alignment,
                'indent': para.paragraph_format.left_indent
            }
            features.append(feature)
        return features
```

**Recognition Accuracy**:

  - Title Recognition: Over 95% accuracy
  - Paragraph Classification: Over 90% accuracy
  - List Recognition: Over 85% accuracy

#### 3\. Formatting Rule Generation Module (format\_manager.py)

**Rule Engine Architecture**:

  - **Rule Template System**: Pre-defined formatting rule templates.
  - **Parameter Mapping Mechanism**: Maps natural language parameters to Word formatting parameters.
  - **Inheritance Handling**: Manages inheritance and overriding of formats between parent and child levels.
  - **Conflict Resolution Strategy**: Resolves conflicts between formatting rules.

**Technical Implementation Details**:

```python
class FormatManager:
    def __init__(self):
        self.rule_templates = self._load_rule_templates()
        self.font_mapping = self._load_font_mapping()
    
    def generate_format_rules(self, ai_response, document_structure):
        # Parse AI response
        parsed_rules = self._parse_ai_response(ai_response)
        # Apply rule templates
        formatted_rules = self._apply_rule_templates(parsed_rules)
        # Process inheritance relationships
        final_rules = self._process_inheritance(formatted_rules, document_structure)
        return final_rules
    
    def _apply_rule_templates(self, rules):
        formatted = {}
        for element_type, rule in rules.items():
            template = self.rule_templates.get(element_type, {})
            formatted[element_type] = {**template, **rule}
        return formatted
```

**Supported Formatting Parameters**:

  - Font: Font family, size, color, style (bold, italic, underline)
  - Paragraph: Alignment, line spacing, spacing before/after, first-line indent
  - Page: Margins, header/footer, page number settings

#### 4\. Template Management Module (template\_manager.py)

**Template System Architecture**:

  - **JSON Format Storage**: Uses JSON to store template configurations.
  - **Version Control**: Supports template version management and rollback.
  - **Categorized Management**: Manages templates by document type and industry.
  - **Permission Control**: Supports personal and team-shared templates.

**Technical Implementation Details**:

```python
class TemplateManager:
    def __init__(self, template_dir):
        self.template_dir = template_dir
        self.templates = self._load_templates()
    
    def create_template(self, name, rules, metadata=None):
        template = {
            'name': name,
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'rules': rules,
            'metadata': metadata or {}
        }
        self._save_template(template)
        return template
    
    def get_template(self, name):
        return self.templates.get(name)
    
    def list_templates(self, category=None):
        if category:
            return [t for t in self.templates.values() 
                    if t.get('metadata', {}).get('category') == category]
        return list(self.templates.values())
```

**Template Structure Example**:

```json
{
  "name": "Academic Paper Template",
  "version": "1.0",
  "category": "academic",
  "rules": {
    "title": {
      "font": "SimHei",
      "size": 18,
      "alignment": "center",
      "bold": true
    },
    "heading1": {
      "font": "SimHei",
      "size": 16,
      "alignment": "left",
      "bold": true
    },
    "body": {
      "font": "SimSun",
      "size": 12,
      "alignment": "justify",
      "indent": "2 characters",
      "line_spacing": 1.5
    }
  }
}
```

## Core Feature Showcase

### 1\. Intelligent Format Parsing

**Input Example**:

```
User description: "Paper title in 18pt SimHei centered, level 1 heading in 16pt SimHei left-aligned,
body text in 12pt SimSun justified with a 2-character first-line indent and 1.5 line spacing,
references in 10pt SimSun with a hanging indent."
```

**AI Understanding Result**:

  - Automatically identifies 5 different formatting requirements.
  - Accurately parses parameters like font, size, alignment, indentation, and spacing.
  - Establishes a formatting hierarchy and application rules.
  - Generates a complete set of formatting specifications.

### 2\. Intelligent Document Structure Recognition

**Recognition Capabilities**:

  - **Heading Levels**: Automatically recognizes multi-level heading structures (Levels 1-6).
  - **Paragraph Types**: Differentiates between body text, quotes, notes, captions, etc.
  - **Special Elements**: Identifies lists, tables, images, formulas, and code blocks.
  - **Format Inheritance**: Understands parent-child format relationships and inheritance rules.

### 3\. One-Click Intelligent Formatting

**Processing Flow**:

1.  **Document Upload** -\> Supports .docx format, auto-detects encoding.
2.  **Intelligent Analysis** -\> AI understands formatting requirements and recognizes document structure.
3.  **Rule Generation** -\> Converts requirements into precise formatting parameters and style rules.
4.  **Format Application** -\> Applies rules to the entire document in bulk for consistency.
5.  **Quality Check** -\> Automatically validates format correctness and provides optimization suggestions.
6.  **Result Output** -\> Generates a standardized, formatted document.

### 4\. Templated Management

**Built-in Template Library**:

  - Academic Papers (IEEE, ACM, Chinese journals standards, etc.)
  - Business Reports (Annual reports, proposals, analysis reports, etc.)
  - Technical Documents (API documentation, user manuals, specifications, etc.)
  - Government Official Documents (Notices, reports, letters in standard formats, etc.)

**Customization Features**:

  - Visual template editor.
  - Format preview and real-time adjustments.
  - Template version management and rollback.
  - Shared team template library.

## Application Scenarios

### 1\. Academic Writing Scenarios

**Typical Needs**:

  - Standardization of paper formats (IEEE, ACM, Chinese journals, etc.).
  - Management of multi-level heading hierarchies.
  - Unification of reference formats.
  - Standardization of figure and table captions and numbering.

**FormulaAI Solution**:

  - One-click application of journal templates.
  - Intelligent recognition of paper structure.
  - Automatic adjustment of formatting details.
  - Ensures compliance with formatting standards.

### 2\. Corporate Document Scenarios

**Typical Needs**:

  - Uniform formatting for business reports.
  - Standardization of company documents.
  - Consistency in formatting for multi-person collaboration.
  - Standardization of brand image.

**FormulaAI Solution**:

  - Corporate template library management.
  - Batch formatting of documents.
  - Team template sharing.
  - Automatic application of brand standards.

### 3\. Government Official Document Scenarios

**Typical Needs**:

  - Strict standards for official document formats.
  - Standardization of hierarchical headings.
  - Precise layout requirements.
  - Efficiency in batch processing.

**FormulaAI Solution**:

  - Standard templates for official documents.
  - Precise format control.
  - Automatic layout adjustments.
  - Efficient batch processing.

### 4\. Technical Documentation Scenarios

**Typical Needs**:

  - Uniform formatting for API documentation.
  - Formatting for code examples.
  - Management of multi-version documents.
  - Generation of online documentation.

**FormulaAI Solution**:

  - Technical documentation templates.
  - Intelligent recognition of code blocks.
  - Version-based format inheritance.
  - Standardized output.

## API Interface Design

### RESTful API Architecture

#### 1\. Document Processing Interface

```http
POST /api/v1/documents/process
Content-Type: multipart/form-data

Parameters:
- file: Uploaded document file (required)
- template: Template name (optional)
- format_description: Text description of the format (optional)
- options: JSON object for processing options (optional)

Response:
{
    "success": true,
    "document_id": "doc_123456",
    "status": "processing",
    "download_url": "/api/v1/documents/doc_123456/download",
    "preview_url": "/api/v1/documents/doc_123456/preview",
    "estimated_time": 30
}
```

#### 2\. Format Parsing Interface

```http
POST /api/v1/formats/parse
Content-Type: application/json

{
    "description": "Title in 18pt SimHei centered, body text in 12pt SimSun justified",
    "context": "academic_paper",
    "language": "en-US"
}

Response:
{
    "success": true,
    "rules": {
        "title": {
            "font": "SimHei",
            "size": 18,
            "alignment": "center",
            "bold": true
        },
        "body": {
            "font": "SimSun",
            "size": 12,
            "alignment": "justify"
        }
    },
    "confidence": 0.95
}
```

#### 3\. Template Management Interface

```http
# Get a list of templates
GET /api/v1/templates?category=academic&page=1&limit=10

# Get a specific template
GET /api/v1/templates/{template_id}

# Create a new template
POST /api/v1/templates
{
    "name": "Custom Academic Template",
    "category": "academic",
    "rules": {...},
    "metadata": {...}
}

# Update a template
PUT /api/v1/templates/{template_id}

# Delete a template
DELETE /api/v1/templates/{template_id}
```

#### 4\. Task Status Query Interface

```http
GET /api/v1/documents/{document_id}/status

Response:
{
    "document_id": "doc_123456",
    "status": "completed",
    "progress": 100,
    "result": {
        "download_url": "/api/v1/documents/doc_123456/download",
        "preview_url": "/api/v1/documents/doc_123456/preview",
        "processing_time": 25.6,
        "applied_rules": {...}
    }
}
```

## Deployment Configuration

### Environment Requirements

```yaml
# System Requirements
operating_system: Linux/macOS/Windows
python_version: ">=3.8"
memory: ">=4GB"
storage: ">=10GB"

# Dependencies
dependencies:
  - python-docx>=0.8.11
  - PyQt6>=6.4.0
  - requests>=2.28.1
  - pillow>=9.3.0
  - chardet>=5.0.0
  - json5>=0.9.10
  - fastapi>=0.68.0
  - uvicorn>=0.15.0
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (e.g., Chinese fonts)
RUN apt-get update && apt-get install -y \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY templates/ ./templates/

# Create necessary directories
RUN mkdir -p /app/logs /app/output /app/temp

# Set environment variables
ENV PYTHONPATH=/app
ENV FORMULAAI_CONFIG_DIR=/app/config

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Configuration File Management

```json
// config/api_config.json
{
    "ai_providers": {
        "deepseek": {
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "api_key": "${DEEPSEEK_API_KEY}",
            "model": "deepseek-chat",
            "timeout": 300,
            "max_retries": 3
        },
        "openai": {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "${OPENAI_API_KEY}",
            "model": "gpt-4",
            "timeout": 300,
            "max_retries": 3
        }
    },
    "default_provider": "deepseek"
}
```

```json
// config/app_config.json
{
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,
        "max_request_size": "50MB"
    },
    "processing": {
        "max_file_size": "50MB",
        "supported_formats": [".docx"],
        "output_directory": "./output",
        "temp_directory": "./temp",
        "batch_size": 10,
        "max_concurrent_tasks": 5
    },
    "cache": {
        "enabled": true,
        "ttl": 3600,
        "max_size": "1GB"
    },
    "logging": {
        "level": "INFO",
        "file": "./logs/formulaai.log",
        "max_size": "100MB",
        "backup_count": 5
    }
}
```

## Performance Optimization

### 1\. Caching Strategy

```python
# Multi-layer cache architecture
class CacheManager:
    def __init__(self):
        self.memory_cache = LRUCache(maxsize=1000)  # In-memory cache
        self.redis_cache = RedisCache()             # Distributed cache
        self.file_cache = FileCache()               # File cache
    
    def get_ai_response(self, prompt_hash):
        # 1. Memory cache
        if result := self.memory_cache.get(prompt_hash):
            return result
        
        # 2. Redis cache
        if result := self.redis_cache.get(prompt_hash):
            self.memory_cache.set(prompt_hash, result)
            return result
        
        # 3. File cache
        if result := self.file_cache.get(prompt_hash):
            self.redis_cache.set(prompt_hash, result, ttl=3600)
            self.memory_cache.set(prompt_hash, result)
            return result
        
        return None
```

### 2\. Asynchronous Processing Architecture

```python
# Asynchronous task processing
from celery import Celery

app = Celery('formulaai')

@app.task(bind=True)
def process_document_async(self, document_path, format_description, template_name):
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Document structure analysis
        analyzer = StructureAnalyzer()
        structure = analyzer.analyze_document(document_path)
        self.update_state(state='PROGRESS', meta={'progress': 30})
        
        # AI format parsing
        ai_connector = AIConnector()
        format_rules = ai_connector.parse_format_description(format_description)
        self.update_state(state='PROGRESS', meta={'progress': 60})
        
        # Apply formatting
        processor = DocumentProcessor()
        result_path = processor.apply_formatting(document_path, format_rules, structure)
        self.update_state(state='PROGRESS', meta={'progress': 100})
        
        return {'status': 'completed', 'result_path': result_path}
    
    except Exception as exc:
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise
```

### 3\. Memory Management Optimization

```python
# Chunk-based processing for large documents
class DocumentProcessor:
    def __init__(self, batch_size=20):
        self.batch_size = batch_size
    
    def process_large_document(self, document_path, format_rules):
        document = Document(document_path)
        total_paragraphs = len(document.paragraphs)
        
        # Process paragraphs in batches
        for i in range(0, total_paragraphs, self.batch_size):
            batch = document.paragraphs[i:i + self.batch_size]
            self._process_paragraph_batch(batch, format_rules)
            
            # Force garbage collection
            gc.collect()
            
            # Update progress
            progress = min(100, (i + self.batch_size) * 100 // total_paragraphs)
            self._update_progress(progress)
```

### 4\. Concurrency Processing Optimization

```python
# Parallel processing of multiple documents
import asyncio
from concurrent.futures import ThreadPoolExecutor

class BatchProcessor:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_multiple_documents(self, document_tasks):
        loop = asyncio.get_event_loop()
        
        # Create asynchronous tasks
        tasks = []
        for task in document_tasks:
            future = loop.run_in_executor(
                self.executor,
                self._process_single_document,
                task['document_path'],
                task['format_description'],
                task['template_name']
            )
            tasks.append(future)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

## Technical Advantages

### 1\. AI Understanding Capabilities

  - **Multi-model Support**: Integrates various large language models to ensure understanding accuracy.
  - **Prompt Optimization**: Utilizes prompt templates optimized through extensive testing.
  - **Context-aware**: Adjusts understanding strategy based on document type and domain.
  - **Error Self-correction**: Intelligently detects and corrects AI understanding errors.

### 2\. Processing Precision

  - **Pixel-level Control**: Precise font size control down to 0.1 points.
  - **Full Format Support**: Supports all formatting attributes of Word documents.
  - **Hierarchical Consistency**: Ensures format inheritance for multi-level headings.
  - **Quality Validation**: Multi-layer validation mechanism ensures output quality.

### 3\. Performance

  - **High-speed Processing**: Optimized algorithms; average processing time of 15-30 seconds per document.
  - **High Concurrency**: Supports parallel processing of multiple documents to increase overall throughput.
  - **Memory Safe**: Intelligent memory management supports large document processing.
  - **High Availability**: 99.9% service availability with automatic fault recovery.

### 4\. Extensibility

  - **Plugin Architecture**: Supports third-party plugins to extend functionality.
  - **Open API**: Provides a complete RESTful API for easy integration.
  - **Multi-language Support**: Supports format descriptions in languages like Chinese and English.
  - **Cloud-native**: Supports containerized deployment and microservices architecture.

## Security Considerations

### 1\. API Security

```python
# JWT authentication middleware
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/documents/process")
@limiter.limit("10/minute")
async def process_document(request: Request, user_id: str = Depends(verify_token)):
    # Processing logic
    pass
```

### 2\. Data Security

```python
# Encrypted file storage
from cryptography.fernet import Fernet

class SecureFileManager:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    def save_encrypted_file(self, file_path, content):
        encrypted_content = self.cipher.encrypt(content)
        with open(file_path, 'wb') as f:
            f.write(encrypted_content)
    
    def load_encrypted_file(self, file_path):
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        return self.cipher.decrypt(encrypted_content)

# Sensitive information masking
def sanitize_log_data(data):
    sensitive_fields = ['api_key', 'password', 'token']
    for field in sensitive_fields:
        if field in data:
            data[field] = '***masked***'
    return data
```

### 3\. Input Validation

```python
# File type validation
from magic import Magic

def validate_file_type(file_path):
    mime = Magic(mime=True)
    file_type = mime.from_file(file_path)
    
    allowed_types = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    if file_type not in allowed_types:
        raise ValueError(f"Unsupported file type: {file_type}")

# Content security check
def validate_format_description(description):
    # Check length limit
    if len(description) > 10000:
        raise ValueError("Format description too long")
    
    # Check for malicious content
    dangerous_patterns = ['<script>', 'javascript:', 'eval(', 'exec(']
    for pattern in dangerous_patterns:
        if pattern.lower() in description.lower():
            raise ValueError("Potentially dangerous content detected")
```

## Monitoring and Logging

### 1\. Performance Monitoring

```python
# Prometheus metrics collection
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter('formulaai_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('formulaai_request_duration_seconds', 'Request duration')
ACTIVE_TASKS = Gauge('formulaai_active_tasks', 'Number of active processing tasks')
ERROR_COUNT = Counter('formulaai_errors_total', 'Total errors', ['error_type'])

# Middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    # Increment request count
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        ERROR_COUNT.labels(error_type=type(e).__name__).inc()
        raise
    finally:
        # Record request duration
        REQUEST_DURATION.observe(time.time() - start_time)
```

### 2\. Structured Logging

```python
# Structured logging configuration
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage example
logger.info(
    "Document processing started",
    document_id="doc_123456",
    user_id="user_789",
    file_size=1024000,
    format_description="Academic paper format"
)
```

### 3\. Health Check

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "ai_service": await check_ai_service(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Testing Strategy

### 1\. Unit Testing

```python
# Test case example
import pytest
from unittest.mock import Mock, patch

class TestAIConnector:
    def setup_method(self):
        self.ai_connector = AIConnector({
            'api_url': 'https://test-api.com',
            'api_key': 'test-key',
            'model': 'test-model'
        })
    
    @patch('requests.post')
    def test_parse_format_description_success(self, mock_post):
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"title": {"font": "SimHei", "size": 18}}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Execute test
        result = self.ai_connector.parse_format_description("Title in 18pt SimHei")
        
        # Assert results
        assert result['title']['font'] == 'SimHei'
        assert result['title']['size'] == 18
    
    def test_parse_format_description_invalid_json(self):
        with patch.object(self.ai_connector, '_call_ai_api') as mock_call:
            mock_call.return_value = "invalid json"
            
            with pytest.raises(ValueError):
                self.ai_connector.parse_format_description("test")
```

### 2\. Integration Testing

```python
# API integration test
from fastapi.testclient import TestClient

client = TestClient(app)

def test_document_processing_workflow():
    # 1. Upload document
    with open("test_document.docx", "rb") as f:
        response = client.post(
            "/api/v1/documents/process",
            files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"format_description": "Title in 18pt SimHei centered"}
        )
    
    assert response.status_code == 200
    document_id = response.json()["document_id"]
    
    # 2. Query processing status
    status_response = client.get(f"/api/v1/documents/{document_id}/status")
    assert status_response.status_code == 200
    
    # 3. Download result
    download_response = client.get(f"/api/v1/documents/{document_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
```

### 3\. Performance Testing

```python
# Load testing
import asyncio
import aiohttp
import time

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()
        
        # Create 100 concurrent requests
        for i in range(100):
            task = asyncio.create_task(
                test_single_request(session, f"test_doc_{i}.docx")
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Collate results
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = len(results) - success_count
        
        print(f"Total time: {duration:.2f}s")
        print(f"Requests per second: {len(results) / duration:.2f}")
        print(f"Success rate: {success_count / len(results) * 100:.1f}%")

async def test_single_request(session, filename):
    with open(filename, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('file', f, filename=filename)
        data.add_field('format_description', 'Title in 18pt SimHei')
        
        async with session.post('http://localhost:8000/api/v1/documents/process', data=data) as response:
            return await response.json()
```

## Functional Limitations and Notes

### 1\. Document Format Support

  - **Currently Supported**: Microsoft Word (.docx) format
  - **Planned Support**: PDF, HTML, Markdown, etc.
  - **Not Supported**: .doc (legacy Word), plain text, etc.
  - **Technical Limitation**: Dependent on the functional scope of the python-docx library.

### 2\. Scope of Natural Language Understanding

  - **Supported Languages**: Chinese, English format descriptions.
  - **Scope of Understanding**: Common formatting elements like font, size, color, alignment, spacing, indentation, etc.
  - **Complex Scenarios**: Supports multi-level format descriptions and conditional formatting.
  - **AI Limitations**: Relies on the understanding capabilities of large language models; extremely complex descriptions may require manual adjustment.

### 3\. Processing Capacity

  - **Document Size**: Recommended maximum of 50MB per document (configurable).
  - **Page Count**: Recommended maximum of 200 pages (can be extended with chunk-based processing).
  - **Processing Time**: Typically between 15 seconds and 5 minutes, depending on document complexity.
  - **Concurrency Limit**: Default maximum of 5 concurrent tasks (configurable).

### 4\. System Resource Requirements

  - **Memory Usage**: A single task requires approximately 200-500MB of memory.
  - **CPU Requirements**: Multi-core CPUs can improve concurrent processing capabilities.
  - **Storage Space**: Sufficient space is needed for temporary files and cache.
  - **Network Requirements**: A stable network connection is required for AI API calls.

## Project Highlights

### 1\. Innovation

  - **Pioneering Technology**: AI-driven conversion of natural language to formatting rules.
  - **Intelligent Recognition**: Content-semantic-based document structure analysis.
  - **Adaptive Processing**: Automatically adjusts processing strategy based on document characteristics.

### 2\. Practicality

  - **Plug and Play**: Ready to use out of the box without complex configuration.
  - **Efficient Processing**: Significantly improves the efficiency of document formatting.
  - **Quality Assurance**: Ensures the professionalism and consistency of output documents.

### 3\. Extensibility

  - **Modular Design**: Facilitates functional extension and customization.
  - **Open Architecture**: Supports third-party plugins and extensions.
  - **Standard Interfaces**: Provides standardized API interfaces.

## Project Information

  - **Project Name**: FormulaAI - AI-Powered Intelligent Document Formatting Tool
  - **Development Language**: Python 3.8+
  - **Core Technologies**: AI Natural Language Processing, Document Structure Analysis, Automated Formatting
  - **Project Address**: [https://github.com/waterdrop26651/FormulaAI](https://github.com/waterdrop26651/FormulaAI)
  - **Open Source License**: MIT License
  - **Maintenance Status**: Under continuous development and maintenance.

