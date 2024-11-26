export function createWebSocket(onMessage, onOpen, onClose, onError) {
  const socket = new WebSocket("ws://127.0.0.1:8000/ws");

  socket.onopen = function () {
    console.log("WebSocket connection established.");
    if (onOpen) onOpen(socket);
  };

  socket.onmessage = function (event) {
    try {
      const message = event.data;
      if (onMessage) onMessage(message);
    } catch (error) {
      console.error("Error parsing WebSocket message:", error);
    }
  };

  socket.onclose = function () {
    console.log("WebSocket connection closed.");
    if (onClose) onClose();
  };

  socket.onerror = function (error) {
    console.error("WebSocket error:", error);
    if (onError) onError(error);
  };

  return socket;
}
