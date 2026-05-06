// Cross-language contract test for the C++ SDK.
//
// Loads the JSON fixtures recorded by the Python contract suite
// (`tests/contract/fixtures/*.json`) and decodes each one through
// the C++ Parse* helpers. If a fixture appears that the C++ SDK
// can't decode, the test fails — the same kind of semantic-drift
// catch the Python and TypeScript contract tests provide.
//
// Build: cl /std:c++17 /EHsc /I..\include test_contract.cpp
// Run:   .\test_contract.exe
//
// Skips gracefully when the fixture directory is missing (CI runs
// the C++ tests independently of Python).

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

#include "sfmapi/client.hpp"
#include "sfmapi/json.hpp"

#define CHECK(cond, msg)                                              \
  do {                                                                \
    if (!(cond)) {                                                    \
      std::fprintf(stderr, "FAIL: %s\n  at %s:%d\n", msg,             \
                   __FILE__, __LINE__);                               \
      std::exit(1);                                                   \
    }                                                                 \
  } while (0)

namespace fs = std::filesystem;

static fs::path FixtureDir() {
  // Walk up from the test exe location until we find tests/contract.
  fs::path here = fs::current_path();
  for (int i = 0; i < 8; ++i) {
    fs::path candidate = here / "tests" / "contract" / "fixtures";
    if (fs::exists(candidate)) return candidate;
    if (here.has_parent_path()) here = here.parent_path();
    else break;
  }
  return {};
}

static sfmapi::HttpResponse FixtureAsResp(const fs::path& p) {
  std::ifstream f(p);
  if (!f) {
    std::fprintf(stderr, "missing fixture: %s\n", p.string().c_str());
    std::exit(1);
  }
  std::stringstream ss;
  ss << f.rdbuf();
  std::string s = ss.str();
  sfmapi::HttpResponse r;
  r.status = 200;
  r.headers["content-type"] = "application/json";
  r.body.assign(s.begin(), s.end());
  return r;
}

static bool HasFixture(const fs::path& dir, const std::string& name) {
  return fs::exists(dir / (name + ".json"));
}

int main() {
  std::cout << "sfmapi C++ contract tests:\n";
  fs::path dir = FixtureDir();
  if (dir.empty()) {
    std::cout << "  (no fixture dir found; skipping)\n";
    return 0;
  }
  std::cout << "  fixtures: " << dir.string() << "\n";

  // ----- capabilities ------------------------------------------------
  if (HasFixture(dir, "capabilities")) {
    auto resp = FixtureAsResp(dir / "capabilities.json");
    auto caps = sfmapi::Client::ParseCapabilities(resp);
    CHECK(caps.schema_version == 1, "capabilities.schema_version == 1");
    CHECK(!caps.backend.name.empty(), "capabilities.backend.name non-empty");
    std::cout << "  capabilities OK (" << caps.features.size()
              << " feature flags)\n";
  }

  // ----- healthz -----------------------------------------------------
  if (HasFixture(dir, "healthz")) {
    auto h = sfmapi::Client::ParseHealthResponse(FixtureAsResp(dir / "healthz.json"));
    CHECK(!h.status.empty(), "healthz.status non-empty");
    std::cout << "  healthz OK (status=" << h.status << ")\n";
  }

  // ----- version -----------------------------------------------------
  if (HasFixture(dir, "version")) {
    auto v = sfmapi::Client::ParseVersionResponse(FixtureAsResp(dir / "version.json"));
    CHECK(!v.sfmapi.empty(), "version.sfmapi non-empty");
    std::cout << "  version OK (sfmapi=" << v.sfmapi << ", backend="
              << (v.backend ? v.backend->name : "(none)") << ")\n";
  }

  // ----- project_get / project_create --------------------------------
  for (const std::string name : {"project_get", "project_create"}) {
    if (!HasFixture(dir, name)) continue;
    auto p = sfmapi::Client::ParseProject(FixtureAsResp(dir / (name + ".json")));
    CHECK(p.project_id.size() == 26, "project_id is a 26-char ULID");
    CHECK(!p.tenant_id.empty(), "tenant_id non-empty");
    CHECK(!p.name.empty(), "project name non-empty");
    CHECK(!p.created_at.empty(), "project.created_at non-empty");
    std::cout << "  " << name << " OK (name=" << p.name << ")\n";
  }

  // ----- project_list as Page<Project> -------------------------------
  if (HasFixture(dir, "project_list")) {
    auto resp = FixtureAsResp(dir / "project_list.json");
    auto page = sfmapi::Client::ParsePage<sfmapi::Project>(
        resp, [](const sfmapi::Json& item) {
          return sfmapi::Client::ProjectFromJson(item);
        });
    for (const auto& p : page.items) {
      CHECK(p.project_id.size() == 26, "page item is a Project");
    }
    std::cout << "  project_list OK (" << page.items.size() << " items)\n";
  }

  // ----- empty page envelope -----------------------------------------
  if (HasFixture(dir, "page_empty")) {
    auto resp = FixtureAsResp(dir / "page_empty.json");
    auto page = sfmapi::Client::ParsePage<sfmapi::Dataset>(
        resp, [](const sfmapi::Json& item) {
          return sfmapi::Client::DatasetFromJson(item);
        });
    CHECK(page.items.empty(), "empty page has empty items");
    std::cout << "  page_empty OK\n";
  }

  // ----- dataset_create ----------------------------------------------
  if (HasFixture(dir, "dataset_create")) {
    auto d = sfmapi::Client::ParseDataset(FixtureAsResp(dir / "dataset_create.json"));
    CHECK(d.dataset_id.size() == 26, "dataset_id is a ULID");
    CHECK(d.project_id.size() == 26, "project_id is a ULID");
    CHECK(!d.name.empty(), "dataset name non-empty");
    CHECK(!d.camera_model.empty(), "camera_model non-empty");
    std::cout << "  dataset_create OK (camera_model=" << d.camera_model << ")\n";
  }

  // ----- error envelopes are JSON-decodable --------------------------
  for (const std::string name : {"error_404_project_missing", "error_422_validation"}) {
    if (!HasFixture(dir, name)) continue;
    auto resp = FixtureAsResp(dir / (name + ".json"));
    // We don't have typed error structs; just confirm the body parses.
    auto j = sfmapi::Json::Parse(std::string(resp.body.begin(), resp.body.end()));
    CHECK(j.is_object(), "error envelope is a JSON object");
    std::cout << "  " << name << " parses OK\n";
  }

  // ----- upload_init -------------------------------------------------
  if (HasFixture(dir, "upload_init")) {
    auto resp = FixtureAsResp(dir / "upload_init.json");
    auto j = sfmapi::Json::Parse(std::string(resp.body.begin(), resp.body.end()));
    CHECK(j.contains("upload_id"), "upload_init has upload_id");
    CHECK(j["upload_id"].as_string().size() == 26, "upload_id is a ULID");
    CHECK(j.contains("state"), "upload_init has state");
    CHECK(j["state"].as_string() == "open", "upload_init.state == open");
    CHECK(j["received_bytes"].as_number() == 0, "upload_init.received_bytes == 0");
    std::cout << "  upload_init OK\n";
  }

  // ----- second 404 envelope (different resource kind) ---------------
  if (HasFixture(dir, "error_404_dataset_missing")) {
    auto resp = FixtureAsResp(dir / "error_404_dataset_missing.json");
    auto j = sfmapi::Json::Parse(std::string(resp.body.begin(), resp.body.end()));
    CHECK(j.is_object(), "dataset 404 envelope is JSON object");
    CHECK(j.contains("status"), "dataset 404 has status");
    CHECK(j["status"].as_number() == 404, "dataset 404 status == 404");
    std::cout << "  error_404_dataset_missing parses OK\n";
  }

  // ----- job_submit (when present) -----------------------------------
  if (HasFixture(dir, "job_submit")) {
    auto js = sfmapi::Client::ParseJobSubmitResponse(
        FixtureAsResp(dir / "job_submit.json"));
    CHECK(js.job_id.size() == 26, "job_id is a ULID");
    std::cout << "  job_submit OK (" << js.task_ids.size() << " tasks)\n";
  }

  // ----- job_accepted_features ---------------------------------------
  if (HasFixture(dir, "job_accepted_features")) {
    auto js = sfmapi::Client::ParseJobSubmitResponse(
        FixtureAsResp(dir / "job_accepted_features.json"));
    CHECK(js.job_id.size() == 26, "job_accepted_features.job_id is a ULID");
    CHECK(js.task_ids.size() >= 1, "at least one task_id");
    for (const auto& t : js.task_ids) {
      CHECK(t.size() == 26, "each task_id is a ULID");
    }
    std::cout << "  job_accepted_features OK (" << js.task_ids.size()
              << " tasks)\n";
  }

  // ----- snapshot_list_empty -----------------------------------------
  if (HasFixture(dir, "snapshot_list_empty")) {
    auto resp = FixtureAsResp(dir / "snapshot_list_empty.json");
    auto j = sfmapi::Json::Parse(std::string(resp.body.begin(), resp.body.end()));
    CHECK(j.contains("seqs"), "snapshot list has seqs");
    CHECK(j["seqs"].as_array().empty(), "empty seqs array");
    CHECK(j.contains("_links"), "snapshot list has _links");
    CHECK(j["_links"]["latest"].is_null(), "_links.latest is null when empty");
    std::cout << "  snapshot_list_empty OK\n";
  }

  std::cout << "all OK\n";
  return 0;
}
