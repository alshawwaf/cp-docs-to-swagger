# Contributing to Check Point API Documentation Viewer

Thank you for your interest in contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome. Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- Any implementation ideas you have

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/cp-docs-to-swagger.git
   cd cp-docs-to-swagger
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure your settings

5. Run the application:
   ```bash
   python run.py
   ```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Testing

Before submitting a PR:
- Test the application locally
- Verify all pages load correctly
- Check that theme switching works
- Test with both Management and GAiA APIs

### Documentation

- Update README.md if you change functionality
- Update DEVELOPER_GUIDE.md for architectural changes
- Add comments to complex code

### Commit Messages

Write clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Add detailed description if needed

## Code of Conduct

Be respectful and constructive in all interactions. We're all here to build something great together.

## Questions?

Feel free to open an issue for any questions about contributing.
