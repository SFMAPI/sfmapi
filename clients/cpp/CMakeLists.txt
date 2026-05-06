cmake_minimum_required(VERSION 3.16)
project(sfmapi_cpp CXX)

# Header-only — consumers just add this to their include path.
add_library(sfmapi_cpp INTERFACE)
target_include_directories(sfmapi_cpp INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_compile_features(sfmapi_cpp INTERFACE cxx_std_17)

option(SFMAPI_CPP_TESTS "Build the sfmapi C++ tests" ON)
if(SFMAPI_CPP_TESTS)
  enable_testing()
  add_executable(test_binary test/test_binary.cpp)
  target_link_libraries(test_binary PRIVATE sfmapi_cpp)
  add_test(NAME test_binary COMMAND test_binary)

  add_executable(test_client test/test_client.cpp)
  target_link_libraries(test_client PRIVATE sfmapi_cpp)
  add_test(NAME test_client COMMAND test_client)
endif()
