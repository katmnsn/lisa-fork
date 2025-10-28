# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import re
from typing import Any, Dict, List, Optional

from lisa.executable import Tool
from lisa.operating_system import Posix
from lisa.util import find_patterns_in_lines


class Sysbench(Tool):
    """
    Sysbench is a scriptable multi-threaded benchmark tool based on LuaJIT.
    It is most frequently used for database benchmarks, but can also be used
    to create arbitrarily complex workloads that do not involve a database server.
    """

    # CPU test results pattern
    # events per second:   9999.99
    CPU_EVENTS_PER_SEC = re.compile(r"events per second:\s+(?P<events>\d+\.\d+)", re.M)

    # Memory test results pattern
    # Total operations: 10485760 (1234567.89 per second)
    MEMORY_OPS_PER_SEC = re.compile(
        r"Total operations:.*\((?P<ops>\d+\.\d+) per second\)", re.M
    )

    # Threads fairness pattern
    # avg: 1.23 / stddev: 0.45
    THREADS_FAIRNESS = re.compile(
        r"avg:\s+(?P<avg>\d+\.\d+).*stddev:\s+(?P<stddev>\d+\.\d+)", re.M
    )

    # Latency patterns
    # min:                                    0.50
    # avg:                                    1.23
    # max:                                   10.45
    # 95th percentile:                        2.34
    LATENCY_MIN = re.compile(r"min:\s+(?P<min>\d+\.\d+)", re.M)
    LATENCY_AVG = re.compile(r"avg:\s+(?P<avg>\d+\.\d+)", re.M)
    LATENCY_MAX = re.compile(r"max:\s+(?P<max>\d+\.\d+)", re.M)
    LATENCY_95TH = re.compile(r"95th percentile:\s+(?P<p95>\d+\.\d+)", re.M)

    @property
    def command(self) -> str:
        return "sysbench"

    @property
    def can_install(self) -> bool:
        return True

    def _install(self) -> bool:
        posix_os = self.node.os
        assert isinstance(posix_os, Posix), f"{posix_os} is not a Posix OS"

        # Install sysbench from package repositories
        posix_os.install_packages("sysbench")
        return self._check_exists()

    def run_cpu_test(
        self,
        max_prime: int = 20000,
        num_threads: int = 1,
        max_time: int = 60,
        test_mode: str = "run",
    ) -> str:
        """
        Run CPU benchmark test.

        Args:
            max_prime: Maximum prime number to calculate (default: 20000)
            num_threads: Number of threads to use (default: 1)
            max_time: Maximum execution time in seconds (default: 60)
            test_mode: Test mode - prepare, run, or cleanup (default: run)

        Returns:
            Test output as string
        """
        cmd = (
            f"cpu --cpu-max-prime={max_prime} "
            f"--threads={num_threads} "
            f"--time={max_time} "
            f"{test_mode}"
        )
        result = self.run(cmd, force_run=True, shell=True)
        result.assert_exit_code()
        return result.stdout

    def run_memory_test(
        self,
        memory_block_size: str = "1K",
        memory_total_size: str = "100G",
        num_threads: int = 1,
        max_time: int = 60,
        test_mode: str = "run",
        memory_oper: str = "write",
    ) -> str:
        """
        Run memory benchmark test.

        Args:
            memory_block_size: Size of memory block (default: 1K)
            memory_total_size: Total size of data to transfer (default: 100G)
            num_threads: Number of threads to use (default: 1)
            max_time: Maximum execution time in seconds (default: 60)
            test_mode: Test mode - prepare, run, or cleanup (default: run)
            memory_oper: Memory operation type - read, write, or none (default: write)

        Returns:
            Test output as string
        """
        cmd = (
            f"memory --memory-block-size={memory_block_size} "
            f"--memory-total-size={memory_total_size} "
            f"--memory-oper={memory_oper} "
            f"--threads={num_threads} "
            f"--time={max_time} "
            f"{test_mode}"
        )
        result = self.run(cmd, force_run=True, shell=True)
        result.assert_exit_code()
        return result.stdout

    def run_threads_test(
        self,
        num_threads: int = 4,
        thread_yields: int = 100,
        thread_locks: int = 2,
        max_time: int = 60,
        test_mode: str = "run",
    ) -> str:
        """
        Run threads benchmark test.

        Args:
            num_threads: Number of threads to use (default: 4)
            thread_yields: Number of yields per thread (default: 100)
            thread_locks: Number of locks per thread (default: 2)
            max_time: Maximum execution time in seconds (default: 60)
            test_mode: Test mode - prepare, run, or cleanup (default: run)

        Returns:
            Test output as string
        """
        cmd = (
            f"threads --threads={num_threads} "
            f"--thread-yields={thread_yields} "
            f"--thread-locks={thread_locks} "
            f"--time={max_time} "
            f"{test_mode}"
        )
        result = self.run(cmd, force_run=True, shell=True)
        result.assert_exit_code()
        return result.stdout

    def run_mutex_test(
        self,
        num_threads: int = 4,
        mutex_num: int = 4096,
        mutex_locks: int = 50000,
        mutex_loops: int = 10000,
        test_mode: str = "run",
    ) -> str:
        """
        Run mutex benchmark test.

        Args:
            num_threads: Number of threads to use (default: 4)
            mutex_num: Number of mutexes (default: 4096)
            mutex_locks: Number of mutex locks per thread (default: 50000)
            mutex_loops: Number of empty loops per lock (default: 10000)
            test_mode: Test mode - prepare, run, or cleanup (default: run)

        Returns:
            Test output as string
        """
        cmd = (
            f"mutex --threads={num_threads} "
            f"--mutex-num={mutex_num} "
            f"--mutex-locks={mutex_locks} "
            f"--mutex-loops={mutex_loops} "
            f"{test_mode}"
        )
        result = self.run(cmd, force_run=True, shell=True)
        result.assert_exit_code()
        return result.stdout

    def parse_cpu_results(self, output: str) -> Dict[str, Any]:
        """
        Parse CPU benchmark results.

        Args:
            output: Sysbench CPU test output

        Returns:
            Dictionary containing parsed metrics
        """
        metrics: Dict[str, Any] = {}

        # Parse events per second
        events_match = find_patterns_in_lines(output, [self.CPU_EVENTS_PER_SEC])
        if events_match and events_match[0]:
            metrics["events_per_second"] = float(events_match[0][0])

        # Parse latency metrics
        metrics.update(self._parse_latency(output))

        return metrics

    def parse_memory_results(self, output: str) -> Dict[str, Any]:
        """
        Parse memory benchmark results.

        Args:
            output: Sysbench memory test output

        Returns:
            Dictionary containing parsed metrics
        """
        metrics: Dict[str, Any] = {}

        # Parse operations per second
        ops_match = find_patterns_in_lines(output, [self.MEMORY_OPS_PER_SEC])
        if ops_match and ops_match[0]:
            metrics["operations_per_second"] = float(ops_match[0][0])

        # Parse latency metrics
        metrics.update(self._parse_latency(output))

        return metrics

    def parse_threads_results(self, output: str) -> Dict[str, Any]:
        """
        Parse threads benchmark results.

        Args:
            output: Sysbench threads test output

        Returns:
            Dictionary containing parsed metrics
        """
        metrics: Dict[str, Any] = {}

        # Parse latency metrics
        metrics.update(self._parse_latency(output))

        # Parse threads fairness
        fairness_match = find_patterns_in_lines(output, [self.THREADS_FAIRNESS])
        if fairness_match and fairness_match[0]:
            metrics["threads_fairness_avg"] = float(fairness_match[0][0])
            metrics["threads_fairness_stddev"] = float(fairness_match[0][1])

        return metrics

    def _parse_latency(self, output: str) -> Dict[str, float]:
        """
        Parse latency statistics from sysbench output.

        Args:
            output: Sysbench test output

        Returns:
            Dictionary containing latency metrics
        """
        latency: Dict[str, float] = {}

        min_match = find_patterns_in_lines(output, [self.LATENCY_MIN])
        if min_match and min_match[0]:
            latency["latency_min_ms"] = float(min_match[0][0])

        avg_match = find_patterns_in_lines(output, [self.LATENCY_AVG])
        if avg_match and avg_match[0]:
            latency["latency_avg_ms"] = float(avg_match[0][0])

        max_match = find_patterns_in_lines(output, [self.LATENCY_MAX])
        if max_match and max_match[0]:
            latency["latency_max_ms"] = float(max_match[0][0])

        p95_match = find_patterns_in_lines(output, [self.LATENCY_95TH])
        if p95_match and p95_match[0]:
            latency["latency_95th_percentile_ms"] = float(p95_match[0][0])

        return latency
