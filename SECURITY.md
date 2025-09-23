# Security Policy

## Supported Versions

VidPipe is currently in active development. Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in VidPipe, please follow these steps:

### 1. **Do Not** Create a Public Issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Send a detailed report to the maintainers via GitHub's private vulnerability reporting feature or by creating a security advisory.

### 3. Include in Your Report

- **Description** of the vulnerability
- **Steps to reproduce** the vulnerability
- **Potential impact** of the vulnerability
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up questions

### 4. Response Timeline

- **Initial Response**: We aim to respond within 48 hours
- **Investigation**: We will investigate and assess the vulnerability
- **Fix Development**: We will work on a fix and coordinate disclosure
- **Public Disclosure**: We will publicly disclose the vulnerability after a fix is available

## Security Considerations

### Dependencies
VidPipe relies on several external dependencies:
- **OpenCV**: For video processing capabilities
- **PyQt6**: For GUI functionality (optional)
- **NumPy**: For numerical operations

We regularly update dependencies to their latest secure versions through our automated dependency update workflow.

### Pipeline Execution
VidPipe executes user-defined pipelines that can:
- Access camera hardware
- Read and write files
- Display windows
- Execute image processing operations

**Important**: Only run pipelines from trusted sources, as they have the same privileges as the Python process running VidPipe.

### File Handling
VidPipe can read and write various file formats:
- Video files (mp4, avi, mov, etc.)
- Image files (jpg, png, etc.)
- Pipeline definition files (.vp)

Ensure that input files come from trusted sources to avoid potential security issues.

## Best Practices for Users

1. **Keep Dependencies Updated**: Regularly update VidPipe and its dependencies
2. **Validate Input**: Be cautious with pipeline files from unknown sources
3. **File Permissions**: Run VidPipe with appropriate file system permissions
4. **Network Security**: Be aware that some functions might access network resources

## Security Improvements

We welcome contributions that improve VidPipe's security:
- Input validation improvements
- Sandboxing capabilities
- Security-focused testing
- Documentation of security considerations

## Contact

For security-related questions or concerns, please:
1. Use GitHub's private vulnerability reporting
2. Create a security advisory on GitHub
3. Contact the maintainers through appropriate channels

Thank you for helping keep VidPipe secure!