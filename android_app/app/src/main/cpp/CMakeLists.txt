cmake_minimum_required(VERSION 3.18.1)
project(memorydebugger)

add_library(memorydebugger SHARED
            memory_access.cpp)

find_library(log-lib log)
target_link_libraries(memorydebugger ${log-lib})