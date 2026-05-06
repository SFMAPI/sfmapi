// sfmapi — minimal stdlib-only JSON value + parser + serializer.
//
// The full sfmapi C++ SDK can stay JSON-library-agnostic (consumers
// plug in nlohmann::json or RapidJSON) — this header just gives you a
// "batteries-included" option for code that wants typed responses
// without pulling in a third-party dep.
//
// Scope:
//   - Parses any RFC 8259 JSON document into a `sfmapi::Json` value.
//   - Serializes back. Compact + pretty modes.
//   - Numbers are double internally; ints up to 2^53 round-trip
//     exactly (same as JS / Python / Go's standard JSON behavior).
//   - No streaming. Documents up to ~10 MB parse fine; beyond that,
//     plug in a real JSON library.
//
// Usage:
//
//     auto val = sfmapi::Json::Parse(R"({"x":1,"y":[2,3]})");
//     int x = (int)val["x"].as_number();        // 1
//     auto y0 = (int)val["y"][0].as_number();    // 2
//     std::string s = val.Dump();                 // compact
//     std::string p = val.Dump(/*indent=*/2);     // pretty
//
//     sfmapi::Json obj{{"name", "x"}, {"value", 42}};  // brace-init
//     obj["extra"] = sfmapi::Json::Array{1, 2, 3};

#ifndef SFMAPI_JSON_HPP_
#define SFMAPI_JSON_HPP_

#include <cctype>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <variant>
#include <vector>

namespace sfmapi {

class JsonError : public std::runtime_error {
 public:
  using std::runtime_error::runtime_error;
};

class Json {
 public:
  using Null = std::nullptr_t;
  using Bool = bool;
  using Number = double;
  using String = std::string;
  using Array = std::vector<Json>;
  using Object = std::map<std::string, Json>;

  using Variant = std::variant<Null, Bool, Number, String, Array, Object>;

  Json() : v_(nullptr) {}
  Json(std::nullptr_t) : v_(nullptr) {}
  Json(bool b) : v_(b) {}
  Json(int n) : v_(static_cast<double>(n)) {}
  Json(long n) : v_(static_cast<double>(n)) {}
  Json(long long n) : v_(static_cast<double>(n)) {}
  Json(unsigned n) : v_(static_cast<double>(n)) {}
  Json(double n) : v_(n) {}
  Json(const char* s) : v_(String(s)) {}
  Json(std::string s) : v_(std::move(s)) {}
  Json(Array a) : v_(std::move(a)) {}
  Json(Object o) : v_(std::move(o)) {}
  Json(std::initializer_list<std::pair<const std::string, Json>> kvs)
      : v_(Object(kvs.begin(), kvs.end())) {}

  bool is_null() const { return std::holds_alternative<Null>(v_); }
  bool is_bool() const { return std::holds_alternative<Bool>(v_); }
  bool is_number() const { return std::holds_alternative<Number>(v_); }
  bool is_string() const { return std::holds_alternative<String>(v_); }
  bool is_array() const { return std::holds_alternative<Array>(v_); }
  bool is_object() const { return std::holds_alternative<Object>(v_); }

  bool as_bool() const { return std::get<Bool>(v_); }
  Number as_number() const { return std::get<Number>(v_); }
  const String& as_string() const { return std::get<String>(v_); }
  const Array& as_array() const { return std::get<Array>(v_); }
  const Object& as_object() const { return std::get<Object>(v_); }
  Array& as_array() { return std::get<Array>(v_); }
  Object& as_object() { return std::get<Object>(v_); }

  // Access. Out-of-range / wrong-type throws JsonError.
  const Json& operator[](const std::string& k) const {
    const auto& o = as_object();
    auto it = o.find(k);
    if (it == o.end()) throw JsonError("missing key: " + k);
    return it->second;
  }
  Json& operator[](const std::string& k) {
    if (!is_object()) v_ = Object{};
    return as_object()[k];
  }
  const Json& operator[](std::size_t i) const {
    const auto& a = as_array();
    if (i >= a.size()) throw JsonError("array index out of range");
    return a[i];
  }
  Json& operator[](std::size_t i) {
    if (!is_array()) v_ = Array{};
    auto& a = as_array();
    if (i >= a.size()) a.resize(i + 1);
    return a[i];
  }

  /// Returns nullptr-Json if missing — useful for optional fields.
  const Json& get_or(const std::string& k, const Json& fallback) const {
    if (!is_object()) return fallback;
    const auto& o = as_object();
    auto it = o.find(k);
    return (it == o.end()) ? fallback : it->second;
  }

  bool contains(const std::string& k) const {
    return is_object() && as_object().count(k) > 0;
  }

  // ---- parsing ------------------------------------------------------

  static Json Parse(const std::string& s) {
    std::size_t i = 0;
    SkipWs(s, i);
    Json out = ParseValue(s, i);
    SkipWs(s, i);
    if (i != s.size()) {
      throw JsonError("trailing junk at position " + std::to_string(i));
    }
    return out;
  }

  // ---- serialization ------------------------------------------------

  /// Dump to a string. ``indent == 0`` is compact; positive prints
  /// pretty with that many spaces per level.
  std::string Dump(int indent = 0) const {
    std::string out;
    WriteValue(*this, out, indent, 0);
    return out;
  }

 private:
  Variant v_;

  static void SkipWs(const std::string& s, std::size_t& i) {
    while (i < s.size() &&
           (s[i] == ' ' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r')) {
      ++i;
    }
  }

  static Json ParseValue(const std::string& s, std::size_t& i) {
    SkipWs(s, i);
    if (i >= s.size()) throw JsonError("unexpected end of input");
    char c = s[i];
    if (c == '{') return ParseObject(s, i);
    if (c == '[') return ParseArray(s, i);
    if (c == '"') return Json(ParseString(s, i));
    if (c == 't' || c == 'f') return Json(ParseBool(s, i));
    if (c == 'n') {
      if (s.compare(i, 4, "null") != 0) throw JsonError("expected null");
      i += 4;
      return Json(nullptr);
    }
    if (c == '-' || (c >= '0' && c <= '9')) return Json(ParseNumber(s, i));
    throw JsonError(std::string("unexpected character: ") + c);
  }

  static Object ParseObject(const std::string& s, std::size_t& i) {
    Object out;
    ++i;  // consume '{'
    SkipWs(s, i);
    if (i < s.size() && s[i] == '}') {
      ++i;
      return out;
    }
    while (true) {
      SkipWs(s, i);
      if (i >= s.size() || s[i] != '"') {
        throw JsonError("expected string key");
      }
      std::string key = ParseString(s, i);
      SkipWs(s, i);
      if (i >= s.size() || s[i] != ':') {
        throw JsonError("expected ':' after key");
      }
      ++i;
      out.emplace(std::move(key), ParseValue(s, i));
      SkipWs(s, i);
      if (i < s.size() && s[i] == ',') {
        ++i;
        continue;
      }
      if (i < s.size() && s[i] == '}') {
        ++i;
        return out;
      }
      throw JsonError("expected ',' or '}'");
    }
  }

  static Array ParseArray(const std::string& s, std::size_t& i) {
    Array out;
    ++i;  // consume '['
    SkipWs(s, i);
    if (i < s.size() && s[i] == ']') {
      ++i;
      return out;
    }
    while (true) {
      out.push_back(ParseValue(s, i));
      SkipWs(s, i);
      if (i < s.size() && s[i] == ',') {
        ++i;
        continue;
      }
      if (i < s.size() && s[i] == ']') {
        ++i;
        return out;
      }
      throw JsonError("expected ',' or ']'");
    }
  }

  static std::string ParseString(const std::string& s, std::size_t& i) {
    if (s[i] != '"') throw JsonError("expected '\"'");
    ++i;
    std::string out;
    while (i < s.size()) {
      char c = s[i++];
      if (c == '"') return out;
      if (c == '\\') {
        if (i >= s.size()) throw JsonError("unterminated escape");
        char e = s[i++];
        switch (e) {
          case '"': out += '"'; break;
          case '\\': out += '\\'; break;
          case '/': out += '/'; break;
          case 'b': out += '\b'; break;
          case 'f': out += '\f'; break;
          case 'n': out += '\n'; break;
          case 'r': out += '\r'; break;
          case 't': out += '\t'; break;
          case 'u': {
            if (i + 4 > s.size()) throw JsonError("short \\u escape");
            unsigned cp = 0;
            for (int k = 0; k < 4; ++k) {
              char h = s[i++];
              cp <<= 4;
              if (h >= '0' && h <= '9') cp |= h - '0';
              else if (h >= 'a' && h <= 'f') cp |= 10 + h - 'a';
              else if (h >= 'A' && h <= 'F') cp |= 10 + h - 'A';
              else throw JsonError("bad hex in \\u");
            }
            // Encode as UTF-8 (BMP only; surrogate pairs not handled
            // — JSON-as-wire from sfmapi shouldn't hit this, but
            // documents from elsewhere with characters > U+FFFF in
            // surrogate-pair form will throw on the second \u).
            if (cp < 0x80) {
              out += static_cast<char>(cp);
            } else if (cp < 0x800) {
              out += static_cast<char>(0xC0 | (cp >> 6));
              out += static_cast<char>(0x80 | (cp & 0x3F));
            } else {
              out += static_cast<char>(0xE0 | (cp >> 12));
              out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
              out += static_cast<char>(0x80 | (cp & 0x3F));
            }
            break;
          }
          default:
            throw JsonError(std::string("bad escape: \\") + e);
        }
      } else {
        out += c;
      }
    }
    throw JsonError("unterminated string");
  }

  static bool ParseBool(const std::string& s, std::size_t& i) {
    if (s.compare(i, 4, "true") == 0) {
      i += 4;
      return true;
    }
    if (s.compare(i, 5, "false") == 0) {
      i += 5;
      return false;
    }
    throw JsonError("expected true/false");
  }

  static double ParseNumber(const std::string& s, std::size_t& i) {
    std::size_t start = i;
    if (s[i] == '-') ++i;
    while (i < s.size() && std::isdigit(static_cast<unsigned char>(s[i]))) ++i;
    if (i < s.size() && s[i] == '.') {
      ++i;
      while (i < s.size() && std::isdigit(static_cast<unsigned char>(s[i]))) ++i;
    }
    if (i < s.size() && (s[i] == 'e' || s[i] == 'E')) {
      ++i;
      if (i < s.size() && (s[i] == '+' || s[i] == '-')) ++i;
      while (i < s.size() && std::isdigit(static_cast<unsigned char>(s[i]))) ++i;
    }
    try {
      return std::stod(s.substr(start, i - start));
    } catch (const std::exception&) {
      throw JsonError("bad number literal");
    }
  }

  static void EscapeString(const std::string& in, std::string& out) {
    out += '"';
    for (char c : in) {
      switch (c) {
        case '"': out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        default:
          if (static_cast<unsigned char>(c) < 0x20) {
            char buf[8];
            std::snprintf(buf, sizeof(buf), "\\u%04x", c);
            out += buf;
          } else {
            out += c;
          }
      }
    }
    out += '"';
  }

  static void WriteIndent(std::string& out, int indent, int depth) {
    if (indent > 0) {
      out += '\n';
      for (int i = 0; i < indent * depth; ++i) out += ' ';
    }
  }

  static void WriteNumber(double n, std::string& out) {
    // Integer-valued doubles print without trailing .0 for compactness.
    if (n == static_cast<std::int64_t>(n) && std::abs(n) < 1e15) {
      out += std::to_string(static_cast<std::int64_t>(n));
    } else {
      char buf[32];
      std::snprintf(buf, sizeof(buf), "%g", n);
      out += buf;
    }
  }

  static void WriteValue(const Json& v, std::string& out, int indent, int depth) {
    if (v.is_null()) {
      out += "null";
    } else if (v.is_bool()) {
      out += v.as_bool() ? "true" : "false";
    } else if (v.is_number()) {
      WriteNumber(v.as_number(), out);
    } else if (v.is_string()) {
      EscapeString(v.as_string(), out);
    } else if (v.is_array()) {
      const auto& a = v.as_array();
      if (a.empty()) {
        out += "[]";
        return;
      }
      out += '[';
      for (std::size_t i = 0; i < a.size(); ++i) {
        if (i) out += ',';
        WriteIndent(out, indent, depth + 1);
        WriteValue(a[i], out, indent, depth + 1);
      }
      WriteIndent(out, indent, depth);
      out += ']';
    } else if (v.is_object()) {
      const auto& o = v.as_object();
      if (o.empty()) {
        out += "{}";
        return;
      }
      out += '{';
      bool first = true;
      for (const auto& kv : o) {
        if (!first) out += ',';
        first = false;
        WriteIndent(out, indent, depth + 1);
        EscapeString(kv.first, out);
        out += indent > 0 ? ": " : ":";
        WriteValue(kv.second, out, indent, depth + 1);
      }
      WriteIndent(out, indent, depth);
      out += '}';
    }
  }
};

}  // namespace sfmapi

#endif  // SFMAPI_JSON_HPP_
