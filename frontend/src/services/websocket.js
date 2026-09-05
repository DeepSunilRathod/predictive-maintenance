export const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/live";

/**
 * Tiny WebSocket wrapper with auto-reconnect (exponential backoff, capped).
 * onMessage receives the parsed JSON payload for every non-"hello" message.
 */
export function connectLiveSocket(onMessage, onStatusChange) {
  let socket;
  let closedByClient = false;
  let attempt = 0;

  function connect() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      attempt = 0;
      onStatusChange?.("connected");
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type !== "hello") onMessage?.(payload);
      } catch (e) {
        console.error("Failed to parse WS message", e);
      }
    };

    socket.onclose = () => {
      onStatusChange?.("disconnected");
      if (!closedByClient) {
        const delay = Math.min(1000 * 2 ** attempt, 15000);
        attempt += 1;
        setTimeout(connect, delay);
      }
    };

    socket.onerror = () => {
      socket.close();
    };
  }

  connect();

  return () => {
    closedByClient = true;
    socket?.close();
  };
}
