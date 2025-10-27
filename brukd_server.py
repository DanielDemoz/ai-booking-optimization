"""
Simple HTTP Server for BRUKD Consultancy Dashboard
Serves the static HTML dashboard without Flask dependencies
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

class BRUKDHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for BRUKD dashboard"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            # Serve the BRUKD dashboard
            self.path = '/brukd_dashboard.html'
        return super().do_GET()
    
    def end_headers(self):
        """Add CORS headers for development"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_brukd_server(port=8080):
    """Start the BRUKD dashboard server"""
    
    print("=" * 60)
    print("BRUKD Consultancy - AI Booking Optimization Dashboard")
    print("=" * 60)
    print(f"Starting server on port {port}...")
    
    try:
        with socketserver.TCPServer(("", port), BRUKDHandler) as httpd:
            print(f"✅ Server running at: http://localhost:{port}")
            print(f"✅ Dashboard available at: http://localhost:{port}")
            print("")
            print("🎯 Features Available:")
            print("   • AI No-Show Predictions")
            print("   • Real-time Analytics Dashboard")
            print("   • Automated Reminder System")
            print("   • PIPEDA Compliance Features")
            print("   • BRUKD Consultancy Branding")
            print("")
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Automatically open browser
            webbrowser.open(f'http://localhost:{port}')
            
            # Start serving
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_brukd_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)

def main():
    """Main function"""
    port = 8080
    
    # Check if port is specified as command line argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8080.")
    
    # Check if BRUKD dashboard file exists
    dashboard_file = Path("brukd_dashboard.html")
    if not dashboard_file.exists():
        print("❌ BRUKD dashboard file not found!")
        print("Please make sure 'brukd_dashboard.html' is in the current directory.")
        sys.exit(1)
    
    start_brukd_server(port)

if __name__ == "__main__":
    main()
