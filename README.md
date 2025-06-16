### RESUMIX

RESUMIX is a tool for generating resumes in various formats. It allows users to create professional resumes quickly and easily.

### Features

- Generate resumes in PDF, HTML, and Markdown formats.
- Customizable templates for different professions.
- Easy to use interface.
- AI-powered resume analysis and optimization.

### Setup and Installation

1. Clone the repository and navigate to the project directory:

   ```bash
   cd resumix
   ```

2. Install the Poetry package manager if you haven't already:

   ```bash
   pip install poetry
   ```

3. Update the Poetry lock file and install dependencies:

   ```bash
   poetry lock
   poetry install
   ```

4. Install required additional packages:

   ```bash
   pip install PyMuPDF==1.22.1 readability-lxml trafilatura
   ```

5. Activate the Poetry environment:

   ```bash
   # For Poetry 2.0+
   source $(poetry env info --path)/bin/activate

   # For older Poetry versions
   poetry shell
   ```

6. Run the application:
   ```bash
   # Make sure to set PYTHONPATH each time you run the app
   export PYTHONPATH=$(pwd):$PYTHONPATH && streamlit run resumix/main.py
   ```

### Troubleshooting

If you encounter import errors:

- Make sure your PYTHONPATH includes the project root directory
- Verify that all dependencies are installed correctly
- Check that you're using the correct version of PyMuPDF (1.22.1 recommended)
- Ensure all imports use the `resumix` package prefix (e.g., `from resumix.utils.logger import logger`)

### Development Notes

When making changes to the codebase:

- All imports should use the `resumix` package prefix (e.g., `from resumix.utils.logger import logger`)
- Section objects have a `raw_text` attribute that should be used when processing text content

### Common Import Issues

This project has a specific import structure. Here are the rules to follow:

1. When importing from the same directory, use direct imports:

   ```python
   # If you're in resumix/tool/tool.py and importing from resumix/tool/agent.py
   from agent import AgentClass
   ```

2. When importing from a different directory but within the resumix package, use relative imports:

   ```python
   # If you're in resumix/tool/tool.py and importing from resumix/utils/logger.py
   from utils.llm_client import LLMClient
   ```

3. When importing from outside the current file's package, use the full path:
   ```python
   # If you're in a test file outside the resumix package
   from resumix.utils.logger import logger
   ```
