cmake_minimum_required(VERSION 3.24)
project(poisson-focus C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -O0")

add_executable(pfocus pfocus.c pfocus.h main.c)
add_executable(pfocus_compeff pfocus.c pfocus.h main_compeff.c)
