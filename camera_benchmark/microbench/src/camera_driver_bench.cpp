#include <algorithm>
#include <chrono>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

// Include configuration headers
#include "config.h"

// Include camera driver headers
#include "camera_driver.hpp"
#include "camera_driver_factory.hpp"
#include "rs_camera_driver.hpp"
#include "virtual_rs_camera_driver.hpp"

// Helper function to parse command line arguments
bool get_arg_bool(int argc, char** argv, const std::string& arg)
{
    for (int i = 1; i < argc; ++i) {
        std::string arg_str(argv[i]);
        if (arg_str.find(arg) == 0) {
            std::string val = arg_str.substr(arg.length() + 1);
            return val == "1" || val == "true";
        }
    }
    return false;
}

// Benchmark function
void benchmark_camera(
    CameraDriver& camera,
    bool enable_depth,
    bool enable_color,
    int duration_seconds
)
{
    // Performance metrics
    std::vector<double> frame_times;
    std::vector<double> depth_processing_times;
    std::vector<double> color_processing_times;

    // Enable streams based on parameters
    if (enable_depth) {
        camera.enable_depth_stream();
    }
    if (enable_color) {
        camera.enable_color_stream();
    }

    // Start pipeline
    camera.pipe_start();

    // Run benchmark for specified duration
    auto start_time = std::chrono::steady_clock::now();
    auto end_time = start_time + std::chrono::seconds(duration_seconds);

    int frame_count = 0;

    while (std::chrono::steady_clock::now() < end_time) {
        auto frame_start = std::chrono::steady_clock::now();

        // Update frames
        bool success = camera.update_frames();
        if (!success) {
            std::cerr << "Failed to update frames" << std::endl;
            break;
        }

        // Process depth frame if enabled
        if (enable_depth) {
            auto depth_start = std::chrono::steady_clock::now();
            cv::Mat depth_frame = camera.get_depth_frame();
            auto depth_end = std::chrono::steady_clock::now();

            if (!depth_frame.empty()) {
                std::chrono::duration<double, std::milli> depth_duration = depth_end - depth_start;
                depth_processing_times.push_back(depth_duration.count());
            }
        }

        // Process color frame if enabled
        if (enable_color) {
            auto color_start = std::chrono::steady_clock::now();
            cv::Mat color_frame = camera.get_color_frame();
            auto color_end = std::chrono::steady_clock::now();

            if (!color_frame.empty()) {
                std::chrono::duration<double, std::milli> color_duration = color_end - color_start;
                color_processing_times.push_back(color_duration.count());
            }
        }

        auto frame_end = std::chrono::steady_clock::now();
        std::chrono::duration<double, std::milli> frame_duration = frame_end - frame_start;
        frame_times.push_back(frame_duration.count());

        frame_count++;
    }

    // Calculate statistics
    double total_time_ms = std::accumulate(frame_times.begin(), frame_times.end(), 0.0);
    double avg_frame_time = total_time_ms / frame_times.size();
    double fps = 1000.0 / avg_frame_time;

    // Calculate min/max/avg for frame times
    double min_frame_time = *std::min_element(frame_times.begin(), frame_times.end());
    double max_frame_time = *std::max_element(frame_times.begin(), frame_times.end());

    // Calculate depth and color processing stats if enabled
    double avg_depth_time = 0.0;
    double avg_color_time = 0.0;

    if (enable_depth && !depth_processing_times.empty()) {
        avg_depth_time =
            std::accumulate(depth_processing_times.begin(), depth_processing_times.end(), 0.0) /
            depth_processing_times.size();
    }

    if (enable_color && !color_processing_times.empty()) {
        avg_color_time =
            std::accumulate(color_processing_times.begin(), color_processing_times.end(), 0.0) /
            color_processing_times.size();
    }

    // Output results in a format that can be parsed by benchkit
    std::cout << "frame_count=" << frame_count << std::endl;
    std::cout << "avg_frame_time_ms=" << avg_frame_time << std::endl;
    std::cout << "min_frame_time_ms=" << min_frame_time << std::endl;
    std::cout << "max_frame_time_ms=" << max_frame_time << std::endl;
    std::cout << "fps=" << fps << std::endl;

    if (enable_depth) {
        std::cout << "avg_depth_processing_ms=" << avg_depth_time << std::endl;
    }

    if (enable_color) {
        std::cout << "avg_color_processing_ms=" << avg_color_time << std::endl;
    }
}

int main(int argc, char** argv)
{
    // Parse command line arguments
    bool enable_depth = get_arg_bool(argc, argv, "--enable_depth");
    bool enable_color = get_arg_bool(argc, argv, "--enable_color");

    // Create appropriate camera driver based on configuration
    std::unique_ptr<CameraDriver> camera;

    // Create camera driver based on DRIVER_TYPE set by CMake
#if DRIVER_TYPE == 0  // Real camera
    try {
        camera = std::make_unique<RSCameraDriver>(enable_color, enable_depth);
        std::cout << "driver_type=RSCameraDriver" << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Failed to initialize RS camera: " << e.what() << std::endl;
        return 1;
    }
#else  // Virtual camera
    camera = std::make_unique<VirtualRSCameraDriver>(
        enable_color, enable_depth, DATASET_PATH, DATASET_NAME
    );
    std::cout << "driver_type=VirtualRSCameraDriver" << std::endl;
#endif

    // Run benchmark
    benchmark_camera(*camera, enable_depth, enable_color, BENCHMARK_DURATION_SECONDS);

    return 0;
}
