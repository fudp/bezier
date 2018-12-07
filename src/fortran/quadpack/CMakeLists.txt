cmake_minimum_required(VERSION 3.1)

project(
  quadpack
  DESCRIPTION "QUADPACK is a FORTRAN 77 library for numerical integration of one-dimensional functions."
  LANGUAGES Fortran
)

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()

add_library(quadpack d1mach.f dqelg.f dqpsrt.f dqk21.f dqagse.f)
set_target_properties(quadpack PROPERTIES Fortran_FORMAT "FIXED")

if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  target_compile_options(quadpack PRIVATE -Wall -fno-second-underscore)
  target_compile_options(quadpack PUBLIC -O3 -funroll-loops)
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  target_compile_options(quadpack PUBLIC -fast)
else()
  message(FATAL_ERROR "gfortran and ifort are the only supported compilers")
endif()
