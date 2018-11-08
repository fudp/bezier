cmake_minimum_required(VERSION 3.1)

project(bezier VERSION 0.9.0
               DESCRIPTION "Library for Bezier curves and triangles"
               LANGUAGES Fortran C)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()

add_library(quadpack src/bezier/quadpack/d1mach.f src/bezier/quadpack/dqelg.f src/bezier/quadpack/dqpsrt.f src/bezier/quadpack/dqk21.f src/bezier/quadpack/dqagse.f)

add_library(bezier src/bezier/types.f90 src/bezier/status.f90 src/bezier/helpers.f90 src/bezier/curve.f90 src/bezier/surface.f90 src/bezier/curve_intersection.f90 src/bezier/surface_intersection.f90)
target_link_libraries(bezier PRIVATE quadpack)
target_include_directories(bezier PUBLIC src/bezier/include)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  target_compile_options(quadpack PRIVATE -Wall -ffixed-form -fno-second-underscore)
  target_compile_options(quadpack PUBLIC -O3 -funroll-loops)
  target_compile_options(bezier PRIVATE -Wall -fno-second-underscore -Wextra -Wno-compare-reals -Wimplicit-interface -fmax-errors=1 -std=f2008 -Werror -march=native)
  target_compile_options(bezier PUBLIC -O3 -funroll-loops)
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  target_compile_options(quadpack PUBLIC -fast)
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()
