cmake_minimum_required(VERSION 3.24)
project(gbm_benchmark C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra")

add_executable(gbm_benchmark main_compeff.c queue.c queue.h trigger.c trigger.h)
