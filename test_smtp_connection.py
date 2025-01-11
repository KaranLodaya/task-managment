import socket
import ssl

# Establish a connection to the SMTP server
try:
    with socket.create_connection(('smtp.gmail.com', 587)) as sock:
        # Wrap the socket with SSL/TLS (STARTTLS)
        context = ssl.create_default_context()
        with context.wrap_socket(sock, server_hostname='smtp.gmail.com') as ssock:
            print(f"SSL/TLS version used: {ssock.version()}")
except Exception as e:
    print(f"Error: {e}")
