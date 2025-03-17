cmake_minimum_required(VERSION 3.10)
project(camera_driver_bench VERSION 1.0)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Configure variables
set(DRIVER_TYPE 0 CACHE STRING "Driver type (0 for real, 1 for virtual)")
set(BENCHMARK_DURATION_SECONDS 5 CACHE STRING "Duration of benchmark in seconds")
set(DATASET_PATH "/home/user/workspace/cppdemo/src/dataset_test_20250311-113433" CACHE STRING "Path to dataset for virtual camera")
set(DATASET_NAME "dataset_test_20250311-113433" CACHE STRING "Name of dataset for virtual camera")
# Configure header file
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/include/config.h.in
    ${CMAKE_BINARY_DIR}/config.h
)

# Find required packages
find_package(OpenCV REQUIRED)
find_package(realsense2 REQUIRED)

# Add subdirectories for dependent libraries
add_subdirectory(deps/camera_driver)

# Include directories
include_directories(
    ${CMAKE_BINARY_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/deps/camera_driver/include
    ${CMAKE_CURRENT_SOURCE_DIR}/deps/camera_driver/deps/frame/include  # Add this line
    ${CMAKE_CURRENT_SOURCE_DIR}/deps/camera_driver/deps/datasethandler/include  # Add this line
)
# Add executable
add_executable(camera_driver_bench ${CMAKE_CURRENT_SOURCE_DIR}/src/camera_driver_bench.cpp)

# Link libraries
target_link_libraries(camera_driver_bench
    camera_driver
    ${OpenCV_LIBS}
    ${realsense2_LIBRARY}
)