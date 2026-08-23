cmake_minimum_required(VERSION 3.22)

project(primus_core CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_library(primus_cpp_core STATIC
    src/core.cpp
)

target_include_directories(primus_cpp_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(primus_test
    src/main.cpp
)

target_link_libraries(primus_test PRIVATE
    primus_cpp_core
)

find_package(pybind11 REQUIRED)

pybind11_add_module(primus_core
    bindings/python_bindings.cpp
)

target_link_libraries(primus_core PRIVATE
    primus_cpp_core
)
