cmake_minimum_required(VERSION 3.1)

project(MyProject VERSION 0.9.0
                  DESCRIPTION "Library for Bezier curves and triangles"
                  LANGUAGES Fortran C)

SET(CMAKE_Fortran_FLAGS "-O3")

add_library(quadpack src/bezier/quadpack/d1mach.f src/bezier/quadpack/dqelg.f src/bezier/quadpack/dqpsrt.f src/bezier/quadpack/dqk21.f src/bezier/quadpack/dqagse.f)

add_library(bezier src/bezier/types.f90 src/bezier/status.f90 src/bezier/helpers.f90 src/bezier/curve.f90 src/bezier/surface.f90 src/bezier/curve_intersection.f90 src/bezier/surface_intersection.f90)
target_link_libraries(bezier PUBLIC quadpack)
target_include_directories(bezier PUBLIC src/bezier/include)
