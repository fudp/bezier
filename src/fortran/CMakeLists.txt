cmake_minimum_required(VERSION 3.1)

project(bezier VERSION 0.9.0
               DESCRIPTION "Library for Bezier curves and triangles"
               LANGUAGES Fortran C)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()

add_library(quadpack quadpack/d1mach.f quadpack/dqelg.f quadpack/dqpsrt.f quadpack/dqk21.f quadpack/dqagse.f)
set_target_properties(quadpack PROPERTIES Fortran_FORMAT "FIXED")

add_library(bezier types.f90 status.f90 helpers.f90 curve.f90 surface.f90 curve_intersection.f90 surface_intersection.f90)
target_link_libraries(bezier PRIVATE quadpack)
target_include_directories(bezier PUBLIC include)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  target_compile_options(quadpack PRIVATE -Wall -fno-second-underscore)
  target_compile_options(quadpack PUBLIC -O3 -funroll-loops)
  target_compile_options(bezier PRIVATE -Wall -fno-second-underscore -Wextra -Wno-compare-reals -Wimplicit-interface -fmax-errors=1 -std=f2008 -Werror -march=native)
  target_compile_options(bezier PUBLIC -O3 -funroll-loops)
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  target_compile_options(quadpack PUBLIC -fast)
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()
