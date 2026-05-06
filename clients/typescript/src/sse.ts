// Minimal SSE parser over a fetch ReadableStream. Yields each `data:`
// payload as a string; the caller does the JSON.parse. Supports
// `id:` lines so consumers can implement Last-Event-ID resume.

export interface SseMessage {
  id: string | undefined;
  event: string | undefined;
  data: string;
}

export async function* iterSse(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<SseMessage> {
  const reader = body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buf = "";
  let cur: { id?: string; event?: string; data: string[] } = { data: [] };
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        if (cur.data.length) {
          yield { id: cur.id, event: cur.event, data: cur.data.join("\n") };
        }
        return;
      }
      buf += decoder.decode(value, { stream: true });
      let idx: number;
      while ((idx = buf.indexOf("\n")) !== -1) {
        const line = buf.slice(0, idx).replace(/\r$/, "");
        buf = buf.slice(idx + 1);
        if (line === "") {
          if (cur.data.length) {
            yield { id: cur.id, event: cur.event, data: cur.data.join("\n") };
          }
          cur = { data: [] };
          continue;
        }
        if (line.startsWith(":")) continue; // SSE comment
        const colon = line.indexOf(":");
        const field = colon === -1 ? line : line.slice(0, colon);
        const value =
          colon === -1 ? "" : line.slice(colon + 1).replace(/^ /, "");
        switch (field) {
          case "id":
            cur.id = value;
            break;
          case "event":
            cur.event = value;
            break;
          case "data":
            cur.data.push(value);
            break;
          // ignore `retry` and others
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
