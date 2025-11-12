#!/usr/bin/env python3
"""
Script to set up SSH tunnel for remote database access
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def setup_ssh_tunnel():
    """Set up SSH tunnel for remote database access"""
    
    if not settings.USE_SSH_TUNNEL:
        print("SSH tunnel is disabled in configuration")
        print("Set USE_SSH_TUNNEL=True to enable")
        return False
    
    if not settings.SSH_HOST:
        print("SSH_HOST is not configured")
        return False
    
    print("="*50)
    print("Setting up SSH Tunnel")
    print("="*50)
    print(f"SSH Host: {settings.SSH_HOST}")
    print(f"SSH Port: {settings.SSH_PORT}")
    print(f"SSH Username: {settings.SSH_USERNAME}")
    print(f"Remote Host: {settings.SSH_TUNNEL_REMOTE_HOST}")
    print(f"Remote Port: {settings.SSH_TUNNEL_REMOTE_PORT}")
    print(f"Local Port: {settings.SSH_TUNNEL_LOCAL_PORT}")
    print("="*50)
    
    # Build SSH command
    ssh_cmd = [
        "ssh",
        "-N",  # No remote command
        "-L",  # Local port forwarding
        f"{settings.SSH_TUNNEL_LOCAL_PORT}:{settings.SSH_TUNNEL_REMOTE_HOST}:{settings.SSH_TUNNEL_REMOTE_PORT}",
        "-p", str(settings.SSH_PORT),
    ]
    
    # Add SSH key if provided
    if settings.SSH_KEY_PATH:
        ssh_cmd.extend(["-i", settings.SSH_KEY_PATH])
    
    # Add username and host
    if settings.SSH_USERNAME:
        ssh_cmd.append(f"{settings.SSH_USERNAME}@{settings.SSH_HOST}")
    else:
        ssh_cmd.append(settings.SSH_HOST)
    
    print(f"\nSSH Command: {' '.join(ssh_cmd)}")
    print("\nStarting SSH tunnel...")
    print("Press Ctrl+C to stop the tunnel")
    
    try:
        # Start SSH tunnel
        process = subprocess.Popen(ssh_cmd)
        
        # Wait a bit for tunnel to establish
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ SSH tunnel established successfully")
            print(f"   Local port {settings.SSH_TUNNEL_LOCAL_PORT} -> {settings.SSH_HOST}:{settings.SSH_TUNNEL_REMOTE_PORT}")
            print("\nYou can now connect to the remote database using:")
            print(f"   postgresql://user:password@localhost:{settings.SSH_TUNNEL_LOCAL_PORT}/database")
            
            # Wait for user to stop
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\nStopping SSH tunnel...")
                process.terminate()
                process.wait()
                print("✅ SSH tunnel stopped")
            
            return True
        else:
            print("❌ SSH tunnel failed to establish")
            return False
            
    except FileNotFoundError:
        print("❌ SSH command not found")
        print("   Please install OpenSSH client")
        return False
    except Exception as e:
        print(f"❌ Error setting up SSH tunnel: {str(e)}")
        return False


def test_tunnel_connection():
    """Test if tunnel is working"""
    import socket
    
    print("\nTesting tunnel connection...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', settings.SSH_TUNNEL_LOCAL_PORT))
        sock.close()
        
        if result == 0:
            print(f"✅ Tunnel port {settings.SSH_TUNNEL_LOCAL_PORT} is accessible")
            return True
        else:
            print(f"❌ Tunnel port {settings.SSH_TUNNEL_LOCAL_PORT} is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tunnel: {str(e)}")
        return False


def main():
    """Main function"""
    if setup_ssh_tunnel():
        test_tunnel_connection()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

