cmake_minimum_required(VERSION 3.1)

project(MyProject VERSION 0.9.0
                  DESCRIPTION "Library for Bezier curves and triangles"
                  LANGUAGES Fortran C)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  if(NOT CCMAKE_Fortran_FLAGS MATCHES "-O3")
    set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -O3")
  endif(NOT CCMAKE_Fortran_FLAGS MATCHES "-O3")
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  if(NOT CCMAKE_Fortran_FLAGS MATCHES "-fast")
    set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -fast")
  endif(NOT CCMAKE_Fortran_FLAGS MATCHES "-fast")
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()

add_library(quadpack src/bezier/quadpack/d1mach.f src/bezier/quadpack/dqelg.f src/bezier/quadpack/dqpsrt.f src/bezier/quadpack/dqk21.f src/bezier/quadpack/dqagse.f)

add_library(bezier src/bezier/types.f90 src/bezier/status.f90 src/bezier/helpers.f90 src/bezier/curve.f90 src/bezier/surface.f90 src/bezier/curve_intersection.f90 src/bezier/surface_intersection.f90)
target_link_libraries(bezier PUBLIC quadpack)
target_include_directories(bezier PUBLIC src/bezier/include)
