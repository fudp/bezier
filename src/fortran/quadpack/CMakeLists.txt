cmake_minimum_required(VERSION 3.1)

project(quadpack DESCRIPTION
        "Library for numerical integration of one-dimensional functions."
        LANGUAGES Fortran)

if(NOT CMAKE_Fortran_COMPILER_ID MATCHES "(GNU|Intel)")
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()

file(GLOB SOURCES *.f)
add_library(quadpack ${SOURCES})
set_target_properties(quadpack PROPERTIES Fortran_FORMAT "FIXED")
if(${BUILD_SHARED_LIBS})
  set_target_properties(quadpack
                        PROPERTIES VERSION
                                   "0.0.1"
                                   SOVERSION
                                   "0.0.1"
                                   POSITION_INDEPENDENT_CODE
                                   ON)
endif()

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  target_compile_options(quadpack
                         PRIVATE -Wall
                                 -fno-second-underscore
                                 -Wextra
                                 -Wno-compare-reals
                                 -Wimplicit-interface
                                 -fmax-errors=1
                                 -std=f2008
                                 -march=native)
  target_compile_options(quadpack PUBLIC -O3 -funroll-loops)
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  target_compile_options(quadpack PUBLIC -fast)
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()
