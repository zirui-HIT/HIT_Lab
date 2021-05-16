cmake_minimum_required(VERSION 3.0.0)
project(badgerDB VERSION 0.1.0)

SET(CMAKE_BUILD_TYPE "Debug")
set(EXECUTABLE_OUTPUT_PATH ../)

aux_source_directory(. SRC_LIST)
aux_source_directory(./exceptions EXCEPTION_LIST)
add_executable(badgerDB ${SRC_LIST} ${EXCEPTION_LIST})

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)