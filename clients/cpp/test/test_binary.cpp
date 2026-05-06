// Tiny smoke test for the binary readers. Mirrors
// `clients/typescript/test/binary.test.ts`. No GoogleTest/Catch
// dependency — just plain assertions so the test runs anywhere with
// a C++17 compiler (Emscripten included).

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <vector>

#include "sfmapi/sfmapi.hpp"

namespace {

template <typename T>
void Push(std::vector<std::uint8_t>& buf, T v) {
  std::uint8_t bytes[sizeof(T)];
  std::memcpy(bytes, &v, sizeof(T));
  buf.insert(buf.end(), bytes, bytes + sizeof(T));
}

void PushBytes(std::vector<std::uint8_t>& buf, std::initializer_list<std::uint8_t> bs) {
  buf.insert(buf.end(), bs.begin(), bs.end());
}

void TestPointsBinary() {
  std::vector<std::uint8_t> buf;
  PushBytes(buf, {'S', 'F', 'M', 'P', '3', 'D', 0, 0});  // magic
  Push<std::uint32_t>(buf, 1);                            // version
  Push<std::uint64_t>(buf, 1);                            // count
  // bbox_min, bbox_max
  for (float v : {0.f, 0.f, 0.f, 1.f, 2.f, 3.f}) Push(buf, v);
  // record
  Push<float>(buf, 1.0f);
  Push<float>(buf, 2.0f);
  Push<float>(buf, 3.0f);
  PushBytes(buf, {255, 128, 64, 0});  // rgb + pad
  Push<std::uint16_t>(buf, 5);        // track_len
  Push<std::uint64_t>(buf, 42);       // point3d_id

  auto parsed = sfmapi::ParsePointsBinary(buf.data(), buf.size());
  assert(parsed.count == 1);
  assert(parsed.records.size() == 1);
  assert(parsed.records[0].xyz[0] == 1.0f);
  assert(parsed.records[0].xyz[1] == 2.0f);
  assert(parsed.records[0].xyz[2] == 3.0f);
  assert(parsed.records[0].rgb[0] == 255);
  assert(parsed.records[0].rgb[1] == 128);
  assert(parsed.records[0].rgb[2] == 64);
  assert(parsed.records[0].track_len == 5);
  assert(parsed.records[0].point3d_id == 42);
  std::cout << "  points-binary OK\n";
}

void TestDepthMap() {
  std::vector<std::uint8_t> buf;
  PushBytes(buf, {'S', 'F', 'M', 'D', 'P', 'T', 'H', 0});
  Push<std::uint32_t>(buf, 1);
  Push<std::uint32_t>(buf, 2);
  Push<std::uint32_t>(buf, 2);
  Push<float>(buf, 1.0f);
  Push<float>(buf, 4.0f);
  Push<std::uint32_t>(buf, 0);  // _pad
  for (float v : {1.f, 2.f, 3.f, 4.f}) Push(buf, v);

  auto parsed = sfmapi::ParseDepthMap(buf.data(), buf.size());
  assert(parsed.width == 2);
  assert(parsed.height == 2);
  assert(parsed.depth_min == 1.0f);
  assert(parsed.depth_max == 4.0f);
  assert(parsed.pixels.size() == 4);
  assert(parsed.pixels[0] == 1.0f && parsed.pixels[3] == 4.0f);
  std::cout << "  depth-binary OK\n";
}

void TestNormalMap() {
  std::vector<std::uint8_t> buf;
  PushBytes(buf, {'S', 'F', 'M', 'N', 'R', 'M', 0, 0});
  Push<std::uint32_t>(buf, 1);
  Push<std::uint32_t>(buf, 1);
  Push<std::uint32_t>(buf, 1);
  Push<float>(buf, 0.0f);
  Push<float>(buf, 0.0f);
  Push<std::uint32_t>(buf, 0);
  for (float v : {0.f, 0.f, 1.f}) Push(buf, v);

  auto parsed = sfmapi::ParseNormalMap(buf.data(), buf.size());
  assert(parsed.width == 1);
  assert(parsed.height == 1);
  assert(parsed.pixels.size() == 3);
  assert(parsed.pixels[2] == 1.0f);
  std::cout << "  normal-binary OK\n";
}

void TestBadMagicRejected() {
  std::vector<std::uint8_t> buf(44, 0);
  bool threw = false;
  try {
    sfmapi::ParsePointsBinary(buf.data(), buf.size());
  } catch (const sfmapi::WireFormatError&) {
    threw = true;
  }
  assert(threw && "expected WireFormatError on bad magic");
  std::cout << "  bad-magic rejected OK\n";
}

void TestSphericalCameraHelper() {
  sfmapi::Camera c;
  c.model = "PINHOLE";
  assert(!c.IsSpherical());
  c.model = sfmapi::kSphericalCameraModel;
  assert(c.IsSpherical());
  std::cout << "  spherical-camera helper OK\n";
}

void TestCapabilitySupports() {
  sfmapi::Capabilities caps;
  caps.features["dense.patch_match_stereo"] = true;
  caps.features["mesh.poisson"] = false;
  assert(caps.Supports("dense.patch_match_stereo"));
  assert(!caps.Supports("mesh.poisson"));
  assert(!caps.Supports("not.a.real.flag"));
  std::cout << "  capabilities helper OK\n";
}

void TestTwoViewGeometryEnumFromWire() {
  using sfmapi::TwoViewGeometryType;
  assert(sfmapi::TwoViewGeometryTypeFromWire("calibrated") ==
         TwoViewGeometryType::kCalibrated);
  assert(sfmapi::TwoViewGeometryTypeFromWire("planar_or_panoramic") ==
         TwoViewGeometryType::kPlanarOrPanoramic);
  assert(sfmapi::TwoViewGeometryTypeFromWire("nonsense") ==
         TwoViewGeometryType::kUndefined);
  std::cout << "  TwoViewGeometryType from wire OK\n";
}

}  // namespace

int main() {
  std::cout << "sfmapi C++ smoke tests:\n";
  TestPointsBinary();
  TestDepthMap();
  TestNormalMap();
  TestBadMagicRejected();
  TestSphericalCameraHelper();
  TestCapabilitySupports();
  TestTwoViewGeometryEnumFromWire();
  std::cout << "all OK\n";
  return 0;
}
