#!/usr/bin/env python3
"""
Simple HTTP server to serve VidPipe web interface
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    # Change to docs directory
    docs_dir = Path(__file__).parent / 'docs'
    if not docs_dir.exists():
        print("Error: docs directory not found")
        sys.exit(1)
    
    os.chdir(docs_dir)
    
    PORT = 8080
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers to allow webcam access
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            super().end_headers()
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"VidPipe Web Server running at http://localhost:{PORT}/")
        print("Open your browser and navigate to the URL above to use VidPipe Web Editor")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == '__main__':
    main()