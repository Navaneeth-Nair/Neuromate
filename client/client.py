#!/usr/bin/env python3
import socket
import struct
import dotenv
import os

dotenv.load_dotenv()
def send_question(question, host='100.86.220.9', port=11434):
    """Send question to server and receive answer."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        
        # Send question length and data
        question_bytes = question.encode('utf-8')
        client_socket.sendall(struct.pack('I', len(question_bytes)))
        client_socket.sendall(question_bytes)
        
        # Receive answer length
        length_data = client_socket.recv(4)
        if not length_data:
            return None
        length = struct.unpack('I', length_data)[0]
        
        # Receive answer
        answer_bytes = b''
        while len(answer_bytes) < length:
            chunk = client_socket.recv(min(4096, length - len(answer_bytes)))
            if not chunk:
                break
            answer_bytes += chunk
        
        answer = answer_bytes.decode('utf-8')
        return answer
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        client_socket.close()

def main():
    """Main client loop."""
    print("Client connected to server")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("You: ").strip()
        if question.lower() == 'quit':
            break
        if not question:
            continue
        
        print("Waiting for response...")
        answer = send_question(question)
        if answer:
            print(f"Assistant: {answer}\n")
        else:
            print("Failed to get response\n")

if __name__ == "__main__":
    main()
