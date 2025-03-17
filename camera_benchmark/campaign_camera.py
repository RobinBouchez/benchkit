#!/usr/bin/env python3
"""
Campaign script for camera driver benchmarks.
"""
import subprocess
import os
import pandas as pd

from kit.camera_benchmark import CameraDriverBench

from benchkit.campaign import CampaignCartesianProduct, CampaignSuite
from benchkit.utils.dir import get_curdir
DATASET_NAME = "dataset_test_20250311-113433"

def can_access_realsense():
    try:
        result = subprocess.run(['ls', '/dev/video*'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               check=False)
        return result.returncode == 0 and len(result.stdout) > 0
    except Exception:
        return False

def main() -> None:
    """Main function for camera driver benchmark campaign."""
    
    # Define path to camera driver implementation
    camera_driver_path = get_curdir(__file__).parent.parent / "deps" / "camera_driver"
    
    # Define dataset path for virtual camera
    dataset_path = get_curdir(__file__).parent.parent / "datasets" / "camera_samples"
    dataset_name = DATASET_NAME

    # Determine which driver types to test
    use_real_camera = can_access_realsense() and os.geteuid() == 0  # Check if running as root
    driver_types = ["0", "1"]# if use_real_camera else ["1"]  # Only test virtual camera if no access
    
    if not use_real_camera:
        print("Warning: No access to RealSense camera or not running as root. Only testing virtual camera.")
    
    
    # Create benchmark campaign
    campaign = CampaignCartesianProduct(
        name="camera_driver_benchmark",
        benchmark=CameraDriverBench(camera_driver_path=camera_driver_path),
        nb_runs=3,
        variables={
            "driver_type": ["0", "1"],  # 0 = Real camera, 1 = Virtual camera
            "enable_depth": [True, False],
            "enable_color": [True, True],
        },
        constants={
            "benchmark_duration_seconds": 1,
            "dataset_path": str(dataset_path),
            "dataset_name": str(dataset_name),
        },
        debug=False,
        gdb=False,
        enable_data_dir=True,
        benchmark_duration_seconds=1,
        pretty={
            "driver_type": {
                "0": "RealSense Camera",
                "1": "Virtual Camera",
            }
        },
    )
    
    # Configure the campaign suite
    suite = CampaignSuite(campaigns=[campaign])
    suite.print_durations()
    suite.run_suite()
    
    # Generate various performance comparison graphs
    
    # Compare FPS between driver types
    suite.generate_graph(
        plot_name="barplot",
        x="driver_type",
        y="fps",
        hue="enable_depth",
        # style="enable_color",
        title="Camera Driver FPS Comparison",
    )
    

    # Compare frame processing times
    suite.generate_graph(
        plot_name="lineplot",
        x="driver_type",
        y="avg_frame_time_ms",
        hue="enable_depth",
        style="enable_color",
        title="Average Frame Processing Time",
    )
    
    # Define a proper dataframe processor function
    def transform_frame_times(dataframe):
        # Create a copy to avoid modifying the original
        result = dataframe.copy()
    
        # Create a new dataframe with the min/max values melted into a single column
        melted_df = pd.melt(
            result,
            id_vars=["driver_type", "enable_depth", "enable_color"],
            value_vars=["min_frame_time_ms", "max_frame_time_ms"],
            var_name="metric",
            value_name="frame_time"
        )
    
        return melted_df

    
    suite.generate_graph(
        plot_name="barplot",
        process_dataframe=transform_frame_times,
        x="driver_type",
        y="frame_time",
        hue="metric",
        title="Min/Max Frame Processing Times",
    )

        # Define a transformation function for initialization times
    def transform_init_times(dataframe):
        # Create a copy to avoid modifying the original
        result = dataframe.copy()
        
        # Create a new dataframe with the initialization time values melted into a single column
        melted_df = pd.melt(
            result,
            id_vars=["driver_type", "enable_depth", "enable_color"],
            value_vars=["stream_config_time_ms", "pipe_start_time_ms", "total_init_time_ms"],
            var_name="initialization_phase",
            value_name="time_ms"
        )
        
        # Clean up the phase names for better display
        melted_df['initialization_phase'] = melted_df['initialization_phase'].replace({
            'stream_config_time_ms': 'Stream Configuration',
            'pipe_start_time_ms': 'Pipeline Startup',
            'total_init_time_ms': 'Total Initialization'
        })
        
        return melted_df

    # Generate graph for camera initialization times
    suite.generate_graph(
        plot_name="barplot",
        process_dataframe=transform_init_times,
        x="driver_type",
        y="time_ms",
        hue="initialization_phase",
        title="Camera Initialization Times",
        ylabel="Time (ms)",
    )


if __name__ == "__main__":
    main()