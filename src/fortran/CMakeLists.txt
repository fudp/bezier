cmake_minimum_required(VERSION 3.1)

project(bezier VERSION 0.9.0 LANGUAGES Fortran C)
set(AUTHOR "Danny Hermes")
set(AUTHOR_DETAILS "daniel.j.hermes@gmail.com")
set(DESCRIPTION "Library for Bezier curves and triangles.")

option(BUILD_SHARED_LIBS "Build shared libraries" ON)

if(NOT CMAKE_Fortran_COMPILER_ID MATCHES "(GNU|Intel)")
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()

add_subdirectory(quadpack)

file(GLOB SOURCES *.f90)
add_library(bezier ${SOURCES} $<TARGET_OBJECTS:quadpack>)
if(${BUILD_SHARED_LIBS})
  set_target_properties(bezier
                        PROPERTIES VERSION
                                   ${bezier_VERSION}
                                   SOVERSION
                                   ${bezier_VERSION}
                                   POSITION_INDEPENDENT_CODE
                                   ON)
endif()

target_include_directories(bezier PUBLIC include)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  target_compile_options(bezier
                         PRIVATE -Wall
                                 -fno-second-underscore
                                 -Wextra
                                 -Wno-compare-reals
                                 -Wimplicit-interface
                                 -fmax-errors=1
                                 -std=f2008
                                 -Werror
                                 -march=native)
  target_compile_options(bezier PUBLIC -O3 -funroll-loops)
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  target_compile_options(bezier PUBLIC -fast)
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()
