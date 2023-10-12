import socket
import os
import torch
from IPython.display import Image  # for displaying images
import random


def load_model(weights_path):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=weights_path)
    return model


def send_response(response):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', server_port))  # Listen on all available network interfaces
    server_socket.listen(1)  # Listen for incoming connections
    print(f"Server listening on port {server_port} for response")
    client_socket, client_address = server_socket.accept()
    client_socket.send(response.encode())
    client_socket.close()

    

def detect_objects(model, img_path):
    results = model(img_path)
    DetectItem=""
    Confidence=0
    HighArea=0
    print("-----------------------------------")
    for det in results.pred[0]:
        class_name = model.names[int(det[5])]
        conf = det[4]
        startX, startY, endX, endY = int(det[0]), int(det[1]), int(det[2]), int(det[3])
        area = (startX-endX)*(startY-endY)
        if area>HighArea:
            HighArea=area
            DetectItem=class_name
            Confidence=conf
        print(f"{class_name}: Confidence: {conf}, Area: {area}")
    print("-----------------------------------")
    print (f"Primary Item Identified : {DetectItem} , Confidence : {Confidence} , Area Occupied : {HighArea}")
    print("-----------------------------------")
    send_response(f"Primary Item : {DetectItem} , Confidence : {Confidence} , Area Occupied : {HighArea}")
    print("Response Sent")
    results.show()  # display results


def receive_image(server_port):

    print(f"Server listening on port {server_port}")

    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('0.0.0.0', server_port))  # Listen on all available network interfaces
            server_socket.listen(1)  # Listen for incoming connections

            client_socket, client_address = server_socket.accept()
            print(f"Client connected: {client_address}")

            # Create a directory to save received images
            if not os.path.exists("received_images"):
                os.makedirs("received_images")

            received_data = b""
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                received_data += data

            # Generate a unique filename for the received image
            image_filename = f"received_images/received_image_{client_address[0]}.jpg"
            # Load your trained weights
            # Save the received data as an image file
            with open(image_filename, 'wb') as image_file:
                image_file.write(received_data)

            print(f"Received image saved as: {image_filename}")
            try:
                client_socket.close()
                server_socket.close()
            except Exception:
                pass
            weights_path = r'C:\Users\HamzaVictus\Documents\StoreItemModel\best.pt'  # replace with your .pt file path
            model = load_model(weights_path)
            
            # Path to your test image
            
            # Perform object detection
            detect_objects(model, image_filename)
   


        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    server_port = 12345  # Choose a port number
    receive_image(server_port)
