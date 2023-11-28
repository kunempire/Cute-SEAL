cmake_minimum_required(VERSION 3.13)

# project name
project(SEALTest VERSION 4.1.1 LANGUAGES CXX)

# If not called from root CMakeLists.txt
if(NOT DEFINED SEAL_BUILD_TEST)
    set(SEAL_BUILD_TEST ON)

    # Import Microsoft SEAL
    find_package(SEAL REQUIRED)

    # Import OpenCV
    find_package(OpenCV REQUIRED)

    # output directory
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)
endif()

if(SEAL_BUILD_TEST)
    # bin-exe name
    add_executable(sealtest) 
   
    # target files you want to apply
    target_sources(sealtest
        PRIVATE
            ${CMAKE_CURRENT_LIST_DIR}/test.cpp
            ${CMAKE_CURRENT_LIST_DIR}/test.hpp
    )

    if(TARGET SEAL::seal)
        target_link_libraries(sealtest PRIVATE SEAL::seal)
    elseif(TARGET SEAL::seal_shared)
        target_link_libraries(sealtest PRIVATE SEAL::seal_shared)
    else()
        message(FATAL_ERROR "Cannot find target SEAL::seal or SEAL::seal_shared")
    endif()

    # Link OpenCV libraries
    target_link_libraries(sealtest PRIVATE ${OpenCV_LIBS})
endif()
