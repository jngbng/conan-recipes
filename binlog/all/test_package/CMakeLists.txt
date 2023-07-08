cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(binlog CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
if(BINLOG_HEADER_ONLY)
    target_link_libraries(${PROJECT_NAME} PUBLIC binlog::binlog_header_only)
else()
    target_link_libraries(${PROJECT_NAME} PUBLIC binlog::binlog)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
