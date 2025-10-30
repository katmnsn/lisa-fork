# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import re
from decimal import Decimal
from typing import Any, Dict

from lisa.executable import Tool
from lisa.operating_system import Posix
from lisa.util import find_patterns_in_lines


class Sysbench(Tool):
    """
    Sysbench is a scriptable multi-threaded benchmark tool for Linux.
    It is commonly used to test CPU, memory, file I/O, and thread performance.
    """

    # CPU benchmark output pattern
    # events per second:  1234.56
    CPU_EVENTS_PATTERN = re.compile(r"events per second:\s+(\d+\.\d+)", re.M)

    # Memory benchmark output patterns
    # Total operations: 104857600 (10485760.00 per second)
    MEMORY_OPS_PATTERN = re.compile(
        r"Total operations:\s+\d+\s+\((\d+\.\d+)\s+per second\)", re.M
    )
    # transferred (10240.00 MiB/sec)
    MEMORY_THROUGHPUT_PATTERN = re.compile(
        r"transferred\s+\((\d+\.\d+)\s+MiB/sec\)", re.M
    )

    # Thread benchmark output pattern
    # events per second:  1234.56
    THREAD_EVENTS_PATTERN = re.compile(r"events per second:\s+(\d+\.\d+)", re.M)

    # File I/O benchmark output patterns
    # read, MiB/s:  123.45
    FILEIO_READ_PATTERN = re.compile(r"read,\s+MiB/s:\s+(\d+\.\d+)", re.M)
    # written, MiB/s:  123.45
    FILEIO_WRITE_PATTERN = re.compile(r"written,\s+MiB/s:\s+(\d+\.\d+)", re.M)

    # General latency patterns
    # avg:    1.23
    LATENCY_AVG_PATTERN = re.compile(r"avg:\s+(\d+\.\d+)", re.M)
    # 95th percentile:  1.23
    LATENCY_95TH_PATTERN = re.compile(r"95th percentile:\s+(\d+\.\d+)", re.M)

    @property
    def command(self) -> str:
        return "sysbench"

    @property
    def can_install(self) -> bool:
        return True

    def _install(self) -> bool:
        assert isinstance(self.node.os, Posix), f"{self.node.os} is not supported"
        self.node.os.install_packages("sysbench")
        return self._check_exists()

    def run_cpu_test(
        self,
        max_prime: int = 20000,
        threads: int = 1,
        time: int = 10,
    ) -> Dict[str, Any]:
        """
        Run CPU performance test using prime number calculation.

        Args:
            max_prime: Maximum prime number to calculate
            threads: Number of worker threads
            time: Test duration in seconds

        Returns:
            Dictionary with events_per_sec metric
        """
        self._log.info(
            f"Running sysbench CPU test: {threads} threads, "
            f"max-prime={max_prime}, duration={time}s"
        )

        cmd = f"cpu --cpu-max-prime={max_prime} --threads={threads} --time={time} run"
        result = self.run(cmd, force_run=True)

        self._log.debug(f"CPU test output: {result.stdout}")

        matched = find_patterns_in_lines(result.stdout, [self.CPU_EVENTS_PATTERN])
        events_per_sec = Decimal(matched[0][0])

        self._log.debug(f"CPU events per second: {events_per_sec}")

        return {
            "events_per_sec": float(events_per_sec),
        }

    def run_memory_test(
        self,
        block_size: str = "1K",
        total_size: str = "10G",
        threads: int = 1,
        time: int = 10,
        access_mode: str = "seq",
        operation: str = "write",
    ) -> Dict[str, Any]:
        """
        Run memory performance test.

        Args:
            block_size: Size of memory block (e.g., '1K', '4K')
            total_size: Total memory size to use (e.g., '1G', '10G')
            threads: Number of worker threads
            time: Test duration in seconds
            access_mode: Access pattern ('seq' or 'rnd')
            operation: Memory operation ('read', 'write', or 'readwrite')

        Returns:
            Dictionary with ops_per_sec and throughput_mib_sec metrics
        """
        self._log.info(
            f"Running sysbench memory test: {threads} threads, "
            f"block-size={block_size}, total-size={total_size}, "
            f"access={access_mode}, op={operation}"
        )

        cmd = (
            f"memory --memory-block-size={block_size} "
            f"--memory-total-size={total_size} --memory-access-mode={access_mode} "
            f"--memory-oper={operation} --threads={threads} --time={time} run"
        )
        result = self.run(cmd, force_run=True)

        self._log.debug(f"Memory test output: {result.stdout}")

        ops_matched = find_patterns_in_lines(result.stdout, [self.MEMORY_OPS_PATTERN])
        throughput_matched = find_patterns_in_lines(
            result.stdout, [self.MEMORY_THROUGHPUT_PATTERN]
        )

        ops_per_sec = Decimal(ops_matched[0][0])
        throughput_mib_sec = Decimal(throughput_matched[0][0])

        self._log.debug(
            f"Memory operations per second: {ops_per_sec}, "
            f"throughput: {throughput_mib_sec} MiB/s"
        )

        return {
            "ops_per_sec": float(ops_per_sec),
            "throughput_mib_sec": float(throughput_mib_sec),
        }

    def run_threads_test(
        self,
        threads: int = 4,
        time: int = 10,
        yields: int = 100,
        locks: int = 8,
    ) -> Dict[str, Any]:
        """
        Run thread scheduler performance test.

        Args:
            threads: Number of worker threads
            time: Test duration in seconds
            yields: Number of yields per lock
            locks: Number of locks

        Returns:
            Dictionary with events_per_sec metric
        """
        self._log.info(
            f"Running sysbench threads test: {threads} threads, "
            f"yields={yields}, locks={locks}, duration={time}s"
        )

        cmd = (
            f"threads --threads={threads} --thread-yields={yields} "
            f"--thread-locks={locks} --time={time} run"
        )
        result = self.run(cmd, force_run=True)

        self._log.debug(f"Threads test output: {result.stdout}")

        matched = find_patterns_in_lines(result.stdout, [self.THREAD_EVENTS_PATTERN])
        events_per_sec = Decimal(matched[0][0])

        self._log.debug(f"Thread events per second: {events_per_sec}")

        return {
            "events_per_sec": float(events_per_sec),
        }

    def run_fileio_test(
        self,
        file_test_mode: str = "rndrw",
        file_total_size: str = "2G",
        file_num: int = 128,
        threads: int = 1,
        time: int = 30,
    ) -> Dict[str, Any]:
        """
        Run file I/O performance test.

        Args:
            file_test_mode: File test mode ('seqwr', 'seqrewr', 'seqrd', 'rndrd',
                           'rndwr', 'rndrw')
            file_total_size: Total size of files
            file_num: Number of files to create
            threads: Number of worker threads
            time: Test duration in seconds

        Returns:
            Dictionary with read_mib_sec, write_mib_sec, and latency metrics
        """
        self._log.info(
            f"Running sysbench file I/O test: mode={file_test_mode}, "
            f"size={file_total_size}, files={file_num}, threads={threads}"
        )

        # Prepare test files
        prepare_cmd = (
            f"fileio --file-test-mode={file_test_mode} "
            f"--file-total-size={file_total_size} --file-num={file_num} prepare"
        )
        self._log.debug(f"Preparing test files: {prepare_cmd}")
        self.run(prepare_cmd, force_run=True)

        # Run the test
        run_cmd = (
            f"fileio --file-test-mode={file_test_mode} "
            f"--file-total-size={file_total_size} --file-num={file_num} "
            f"--threads={threads} --time={time} run"
        )
        result = self.run(run_cmd, force_run=True)

        self._log.debug(f"File I/O test output: {result.stdout}")

        # Parse results
        metrics: Dict[str, Any] = {}

        read_matched = find_patterns_in_lines(
            result.stdout, [self.FILEIO_READ_PATTERN], True
        )
        if read_matched and read_matched[0]:
            metrics["read_mib_sec"] = float(Decimal(read_matched[0][0]))

        write_matched = find_patterns_in_lines(
            result.stdout, [self.FILEIO_WRITE_PATTERN], True
        )
        if write_matched and write_matched[0]:
            metrics["write_mib_sec"] = float(Decimal(write_matched[0][0]))

        latency_avg_matched = find_patterns_in_lines(
            result.stdout, [self.LATENCY_AVG_PATTERN], True
        )
        if latency_avg_matched and latency_avg_matched[0]:
            metrics["latency_avg_ms"] = float(Decimal(latency_avg_matched[0][0]))

        latency_95th_matched = find_patterns_in_lines(
            result.stdout, [self.LATENCY_95TH_PATTERN], True
        )
        if latency_95th_matched and latency_95th_matched[0]:
            metrics["latency_95th_ms"] = float(Decimal(latency_95th_matched[0][0]))

        # Cleanup test files
        cleanup_cmd = (
            f"fileio --file-test-mode={file_test_mode} "
            f"--file-total-size={file_total_size} --file-num={file_num} cleanup"
        )
        self._log.debug(f"Cleaning up test files: {cleanup_cmd}")
        self.run(cleanup_cmd, force_run=True, no_error_log=True)

        self._log.debug(f"File I/O metrics: {metrics}")

        return metrics
