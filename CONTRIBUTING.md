# Contributing to VidPipe

Thank you for your interest in contributing to VidPipe! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yossideutsch1973/vidpipe.git
   cd vidpipe
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install  # For frontend development
   ```

3. **Run tests:**
   ```bash
   make test
   npm run build  # Build frontend
   ```

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   make test                                    # Run test suite
   python main.py --cli -c "your -> pipeline"  # Test CLI
   python main.py --gui                        # Test GUI (if applicable)
   ```

4. **Run code quality checks:**
   ```bash
   black --check .          # Code formatting
   isort --check-only .     # Import sorting
   flake8 .                 # Linting
   mypy vidpipe/            # Type checking
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and create a PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting (line length: 88)
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Add type hints where possible
- Write clear, descriptive commit messages

## Testing

- Write tests for new functionality in the `tests/` directory
- Use pytest for Python tests
- Ensure all tests pass before submitting a PR
- Include both unit tests and integration tests where appropriate
- Test GUI components with pytest-qt when applicable

## Areas for Contribution

### Core Language Features
- New function implementations in `vidpipe/functions.py`
- Parser improvements for new syntax
- Runtime optimizations

### GUI Enhancements
- New editor features
- Better visualization components
- Improved user experience

### Documentation
- Code documentation and docstrings
- Usage examples
- Tutorial content

### Testing & Quality
- Additional test coverage
- Performance tests
- Code quality improvements

## Function Development

When adding new video processing functions:

1. **Add the function to `vidpipe/functions.py`:**
   ```python
   def your_function(frame, param1=default_value):
       # Implementation
       return processed_frame
   
   # Register the function
   function_registry.register(
       "your-function",
       your_function,
       parameters={"param1": "description"},
       description="Function description"
   )
   ```

2. **Add tests in `tests/`:**
   ```python
   def test_your_function():
       # Test implementation
       pass
   ```

3. **Update documentation as needed**

## Reporting Issues

- Use the issue templates provided
- Include reproduction steps
- Provide environment information
- Include error messages and stack traces

## Questions?

- Open an issue for questions about development
- Check existing issues and documentation first
- Be respectful and constructive in discussions

## License

By contributing to VidPipe, you agree that your contributions will be licensed under the same license as the project.