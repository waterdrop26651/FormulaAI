# FormulaAI - AI-Powered Document Formatting Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project Overview

FormulaAI is an AI-powered intelligent document formatting tool that automatically analyzes unformatted Word document structures and applies professional formatting based on user-configured rules. This tool is particularly suitable for academic papers, research reports, technical documents, and other documents requiring standardized formatting.

**Acknowledgments**: This project builds upon the project structure and partial code from `https://github.com/chenningling/AIPoliDoc`.

## Key Features

- **Intelligent Document Structure Analysis**: Leverages AI capabilities to analyze unformatted document structures, automatically identifying titles, abstracts, keywords, body text, and other content
- **Formatting Rules Management**:
  - Supports preset templates and custom formatting rules
  - Provides multiple preset templates (academic paper format, research reports, etc.)
  - Customizable fonts, paragraphs, spacing, and other detailed formatting parameters
- **Automatic Formatting**: Automatically formats documents based on identified structure and formatting rules
- **Multiple AI API Support**:
  - Supports configuration of various AI API interfaces
  - Default support for DeepSeek API
  - Extensible support for other AI services
- **User-Friendly Interface**:
  - Intuitive graphical interface operation
  - Real-time formatting preview
  - Template editing and management support
- **Detailed Logging**: Provides comprehensive processing logs and progress display

## System Requirements

- **Operating System**:
  - Windows 10/11
  - macOS 10.15+
- **Python Environment**:
  - Python 3.8 or higher
- **Dependencies**:
  - python-docx >= 0.8.11 (Word document processing)
  - PyQt6 >= 6.4.0 (GUI interface)
  - requests >= 2.28.1 (HTTP requests)
  - pillow >= 9.3.0 (Image processing)
  - chardet >= 5.0.0 (Character encoding detection)
  - json5 >= 0.9.10 (JSON processing)

## Architecture Design

### V1 vs V2 Architecture Comparison

FormulaAI has undergone a major architectural refactoring from V1 to V2, following Linus Torvalds' "good taste" design principles:

#### V1 Architecture (Traditional Monolithic Design)
- **Single Main Window**: All functionality concentrated in one complex main window class
- **Tightly Coupled Design**: UI components mixed with business logic, difficult to maintain
- **Complex State Management**: Multi-layered nested conditional judgments and state control
- **Over 3 Levels of Indentation**: Violates simplicity principles, poor code readability

#### V2 Architecture (Modular Refactoring)
Comprehensive refactoring based on Linus "good taste" principles:

**1. Eliminate Special Cases**
- Refactored complex conditional branches into unified data flow
- Each component handles only one responsibility, eliminating edge cases

**2. Simplified Data Structures**
- Dual-panel layout: Document Management + Template Settings
- Event-driven architecture: Panels communicate through signals
- Single data source: Configuration manager unified state management

**3. Modular Design**
```
src/ui/
├── main_window_v2.py    # Refactored main window (clean architecture)
├── panels/              # Independent panel modules
│   ├── document_panel.py    # Document management panel
│   ├── template_panel.py    # Template settings panel
│   └── status_panel.py      # Status display panel
└── main_window.py       # V1 main window (backward compatibility)
```

**4. Core Principles Implementation**
- **"Never break userspace"**: V1 and V2 coexist, ensuring backward compatibility
- **"Simplicity obsession"**: No more than 3 levels of indentation, single responsibility per function
- **"Pragmatism"**: Solve real problems, don't pursue theoretical perfection

### Technical Architecture Advantages

#### V2 Improvements over V1:

1. **Memory Safety**
   - Batch processing mechanism: Prevents memory overflow for large documents
   - Defensive programming: Safety checks for every operation
   - Garbage collection optimization: Timely release of unnecessary objects

2. **Stability Enhancement**
   - Eliminate segmentation faults: Through safe font handling and object validation
   - Error isolation: Single component failure doesn't affect the whole system
   - Graceful degradation: Automatically uses default configuration when problems occur

3. **Maintainability**
   - Module independence: Each panel can be developed and tested independently
   - Clear interfaces: Components communicate through well-defined signals
   - Clean code: Follows "good taste" principles, easy to understand and modify

## Project Structure

```
FormulaAI/
├── config/                # Configuration files directory
│   ├── api_config.json   # AI API configuration
│   ├── app_config.json   # Application configuration
│   ├── font_mapping.json # Font mapping configuration
│   └── templates/        # Formatting templates directory
├── src/                  # Source code directory
│   ├── core/            # Core functionality modules
│   │   ├── ai_connector.py     # AI service connector
│   │   ├── doc_processor.py    # Document processor (V2 optimized)
│   │   ├── format_manager.py   # Format manager
│   │   ├── structure_analyzer.py# Structure analyzer
│   │   └── text_template_parser.py # Text parser
│   ├── ui/              # User interface modules
│   │   ├── main_window_v2.py   # V2 main window (recommended)
│   │   ├── main_window.py      # V1 main window (compatibility)
│   │   ├── panels/            # V2 panel modules
│   │   │   ├── document_panel.py
│   │   │   ├── template_panel.py
│   │   │   └── status_panel.py
│   │   ├── template_editor.py  # Template editor
│   │   └── api_config_dialog.py# API configuration dialog
│   └── utils/           # Utility modules
│       ├── font_manager.py    # Font manager (V2 optimized)
│       ├── config_manager.py  # Configuration manager
│       └── logger.py         # Logging system
├── main.py              # Main program entry (uses V2 by default)
└── requirements.txt     # Dependencies list
```

## Installation

1. Clone the project:
   ```bash
   git clone https://github.com/waterdropjack/FormulaAI.git
   cd FormulaAI
   ```

2. Install Python environment (if not already installed)

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. First-time setup requires AI API configuration:
   - Copy `config/api_config.example.json` to `config/api_config.json`
   - Fill in your API configuration in `api_config.json`:
     ```json
     {
         "api_url": "https://your-api-endpoint.com/v1/chat/completions",
         "api_key": "your-api-key-here",
         "model": "deepseek-chat"
     }
     ```

2. Application configuration:
   - Configure save paths, window size, etc. in `config/app_config.json`
   - Configure font mapping relationships in `config/font_mapping.json`

## Usage Instructions

1. Start the program:
   ```bash
   python main.py
   ```

2. Basic usage workflow:
   - Select the Word document to be formatted
   - Choose or customize a formatting template
   - Click the "Start Formatting" button
   - Wait for formatting to complete and view results

3. Template management:
   - Create, edit, and delete templates in the template editor
   - Each template can set formats for different level headings, body text, etc.
   - Supports importing and exporting template configurations

4. Important notes:
   - First-time use requires AI API configuration
   - Recommend backing up original documents before formal formatting
   - If problems occur, check log files for details

## Frequently Asked Questions

1. API configuration issues:
   - Ensure API key is correct
   - Check network connection
   - Confirm API service availability

2. Font issues:
   - Ensure system has fonts used in templates installed
   - Configure font alternatives in `font_mapping.json`

3. Formatting effect issues:
   - Check if document structure is standardized
   - Adjust formatting parameters in templates
   - Check logs to understand AI recognition results

## Contributing

Welcome to submit Issues and Pull Requests to help improve the project. Before submitting code, please ensure:

1. Code follows project coding standards
2. Added necessary comments and documentation
3. Passed all test cases

## License

This project is licensed under the MIT License. See the LICENSE file for details.
