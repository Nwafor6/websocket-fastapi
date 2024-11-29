from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.clients: List[str] = []

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """
        Accept the connection and save the client id
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket

        await websocket.send_text(f"List of users: {self.clients}")
        self.clients.append(client_id)

    async def disconnect(self, client_id: str):
        """
        disconnect user
        """
        print("Helooooo")
        if client_id in self.clients:
            del self.active_connections[client_id]
            self.clients.remove(client_id)

    async def send_personal_message(self, message: str, sender: str, recipient: str):
        """
        Send a personal message to a specific user

        Args:
            message (str): The message to send
            sender (str): Username of the sender
            recipient (str): Username of the recipient
        """
        if recipient in self.active_connections:
            recipient_socket = self.active_connections[recipient]
            await recipient_socket.send_text(f"[PM from {sender}]: {message}")
        else:
            # Optional: If recipient is not online, you might want to handle this
            print(f"User {recipient} is not connected")

    async def broadcast(self, message: str, sender: str):
        """
        Send a message to all connected users

        Args:
            message (str): The message to broadcast
            sender (str): Username of the sender
        """
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(f"[Broadcast from {sender}]: {message}")
            except Exception:
                self.disconnect(client_id)
