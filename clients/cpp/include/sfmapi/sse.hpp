// sfmapi — SSE (Server-Sent Events) buffered parser.
//
// True streaming requires a `StreamingTransport` callback distinct
// from the one-shot HTTP `Transport`; that's a deliberate non-goal
// here. What this header DOES give you: a parser for an already-
// buffered SSE response body, so you can drive the SSE parser yourself
// (e.g. with libcurl's CURLOPT_WRITEFUNCTION accumulating into a
// std::string and parsing periodically).
//
// Wire format (per WHATWG / MDN):
//
//     id: <int>
//     event: <type>
//     data: <line>
//     data: <continuation>
//     <blank line ends the message>
//
// `ParseSseEvents(body)` returns a `vector<SseEvent>` where each
// event has the merged `data` (newline-joined per spec) and any
// `id` / `event` fields seen.

#ifndef SFMAPI_SSE_HPP_
#define SFMAPI_SSE_HPP_

#include <cstring>
#include <string>
#include <vector>

namespace sfmapi {

struct SseEvent {
  std::string id;        // empty if not specified
  std::string event;     // empty if not specified ("message" by convention)
  std::string data;      // possibly multi-line
};

inline std::vector<SseEvent> ParseSseEvents(const std::string& body) {
  std::vector<SseEvent> out;
  SseEvent cur;
  bool have_data = false;

  std::size_t i = 0;
  while (i < body.size()) {
    // Read one line up to '\n' (consume CR if present).
    std::size_t line_end = i;
    while (line_end < body.size() && body[line_end] != '\n') ++line_end;
    std::size_t raw_end = line_end;
    if (raw_end > i && body[raw_end - 1] == '\r') --raw_end;
    std::string line = body.substr(i, raw_end - i);
    i = line_end + 1;  // skip the '\n'

    if (line.empty()) {
      if (have_data) {
        out.push_back(std::move(cur));
        cur = SseEvent{};
        have_data = false;
      }
      continue;
    }
    if (line[0] == ':') continue;  // SSE comment line

    auto colon = line.find(':');
    std::string field, value;
    if (colon == std::string::npos) {
      field = line;
    } else {
      field = line.substr(0, colon);
      // Spec: a single leading space after the colon is stripped.
      std::size_t vs = colon + 1;
      if (vs < line.size() && line[vs] == ' ') ++vs;
      value = line.substr(vs);
    }
    if (field == "data") {
      if (!cur.data.empty()) cur.data += '\n';
      cur.data += value;
      have_data = true;
    } else if (field == "event") {
      cur.event = value;
    } else if (field == "id") {
      cur.id = value;
    }
    // unknown fields ignored per spec
  }
  if (have_data) out.push_back(std::move(cur));
  return out;
}

}  // namespace sfmapi

#endif  // SFMAPI_SSE_HPP_
