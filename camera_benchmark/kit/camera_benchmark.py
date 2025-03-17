#!/usr/bin/env python3
# Copyright (C) 2024
# SPDX-License-Identifier: MIT
"""
Benchkit support for camera driver benchmarks.
"""
from typing import Any, Dict, List
import pathlib
import os
import subprocess

from benchkit.benchmark import Benchmark
from benchkit.utils.dir import get_curdir, parentdir
from benchkit.platforms import get_current_platform as get_platform


class CameraDriverBench(Benchmark):
    """Benchmark object for camera driver performance benchmark."""

    def __init__(self, camera_driver_path: pathlib.Path) -> None:
        """Initialize the benchmark object.
        
        Args:
            camera_driver_path: Path to the camera_driver directory
        """

        super().__init__(
                    command_wrappers=(),      # Empty tuple for no command wrappers
        command_attachments=(),   # Empty tuple for no command attachments
        shared_libs=(),           # Empty tuple for no shared libraries
        pre_run_hooks=(),         # Empty tuple for no pre-run hooks
        post_run_hooks=(),        # Empty tuple for no post-run hooks
        ) 

        self._camera_driver_path = camera_driver_path
        script_path = get_curdir(__file__)
        bench_path = parentdir(path=script_path, levels=1) / "microbench"
        
        self._bench_src_path = bench_path
        self._build_dir = bench_path / "build"
        
        self.platform = get_platform()
        
    @property
    def bench_src_path(self) -> pathlib.Path:
        return self._bench_src_path
    
    @staticmethod
    def get_build_var_names() -> List[str]:
        return [
            "driver_type",
            "benchmark_duration_seconds",
            "dataset_path"
        ]
    
    @staticmethod
    def get_run_var_names() -> List[str]:
        return [
            "enable_depth",
            "enable_color"
        ]
    
    @staticmethod
    def get_tilt_var_names() -> List[str]:
        return []
    
    def prebuild_bench(self, benchmark_duration_seconds: int) -> None:
        """Prepare the benchmark by creating the build directory.
        
        Args:
            benchmark_duration_seconds: Duration in seconds of each benchmark run
        """
        os.makedirs(self._build_dir, exist_ok=True)
    
    def build_bench(self,
                    driver_type: str,
                    benchmark_duration_seconds: int,
                    **kwargs) -> None:
        """Build the benchmark with the given parameters."""
        dataset_path = "/home/user/workspace/cppdemo/benchkit/camera_benchmark/datasets/camera_samples"
        # dataset_path = kwargs.get("dataset_path", "/home/workspace/cppdemo/benchkit/camera_benchmark/datasets/camera_samples/dataset_test_20250311-113433")
        # dataset_name = "dataset_test_20250311-113433"
        dataset_name = kwargs.get("dataset_name", "dataset_test_20250311-113433")
        os.makedirs(self._build_dir, exist_ok=True)

        # Build the benchmark with CMake
        cmake_command = [
            "cmake",
            f"-DDRIVER_TYPE={driver_type}",
            f"-DBENCHMARK_DURATION_SECONDS={benchmark_duration_seconds}",
            f"-DDATASET_PATH={dataset_path}",
            f"-DDATASET_NAME={dataset_name}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-G", "Unix Makefiles",
            str(self._bench_src_path) 
        ]

        environment = self._preload_env(**kwargs)
        wrapped_cmd, wrapped_env = self._wrap_command(cmake_command, environment, **kwargs)

        self.run_bench_command(
            run_command=cmake_command,
            wrapped_run_command=wrapped_cmd,
            current_dir=self._build_dir,
            environment=environment,
            wrapped_environment=wrapped_env,
            print_output=True
        )

        # Run make command
        make_command = ["make", "-j4"]
        wrapped_cmd, wrapped_env = self._wrap_command(make_command, environment, **kwargs)

        self.run_bench_command(
            run_command=make_command,
            wrapped_run_command=wrapped_cmd,
            current_dir=self._build_dir,
            environment=environment,
            wrapped_environment=wrapped_env,
            print_output=True
        )

    def single_run(self,
                   enable_depth: bool,
                   enable_color: bool,
                   **kwargs) -> str:
        """Run a single benchmark instance."""
        run_command = [
            "./camera_driver_bench",
            f"--enable_depth={1 if enable_depth else 0}",
            f"--enable_color={1 if enable_color else 0}"
        ]

        environment = self._preload_env(enable_depth=enable_depth, enable_color=enable_color, **kwargs)
        wrapped_run_command, wrapped_environment = self._wrap_command(run_command=run_command, environment=environment, **kwargs)
        
        output = self.run_bench_command(
            run_command=run_command,
            wrapped_run_command=wrapped_cmd,
            current_dir=self._build_dir,
            environment=environment,
            wrapped_environment=wrapped_env,
            print_output=True
        )

        return output
    
    def clean_bench(self) -> None:
        """Clean the benchmark build directory."""
        if self._build_dir.exists():
            subprocess.run(["rm", "-rf", str(self._build_dir)])
    
    def single_run(self,
                   enable_depth: bool,
                   enable_color: bool,
                   **kwargs) -> str:
        """Run a single benchmark instance.
        
        Args:
            enable_depth: Whether to enable the depth stream
            enable_color: Whether to enable the color stream
            
        Returns:
            The benchmark output
        """

        run_command = [
            "./camera_driver_bench",
            f"--enable_depth={1 if enable_depth else 0}",
            f"--enable_color={1 if enable_color else 0}"
        ]
    

        environment = self._preload_env(enable_depth=enable_depth, enable_color=enable_color, **kwargs)
        wrapped_run_command, wrapped_environment = self._wrap_command(run_command=run_command, environment=environment, **kwargs)
    
        output = self.run_bench_command(
            run_command=run_command,
            wrapped_run_command=wrapped_run_command,
            current_dir=self._build_dir,
            environment=environment,
            wrapped_environment=wrapped_environment,
            print_output=True
        )
        
        return output
    
    def parse_output_to_results(self,
                               command_output: str,
                               run_variables: Dict[str, Any],
                               **kwargs) -> Dict[str, Any]:
        """Parse the benchmark output to extract results.
        
        Args:
            command_output: Output of the benchmark command
            run_variables: Variables used for the run
            
        Returns:
            Dictionary of benchmark results
        """
        results = {}
        
        for line in command_output.strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                try:
                    results[key] = float(value)
                except ValueError:
                    results[key] = value
        
        # Add run parameters to results
        results.update(run_variables)
        
        return results
