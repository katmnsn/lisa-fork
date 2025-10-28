# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import re
from decimal import Decimal
from typing import Any, Dict, List, cast

from lisa.executable import Tool
from lisa.operating_system import Posix
from lisa.util import find_patterns_in_lines


class Sysbench(Tool):
    # Example output patterns from sysbench:
    # CPU test:
    #   events per second:  1234.56
    # Memory test:
    #   Total operations: 123456789 (12345678.90 per second)
    #   1234.56 MiB transferred (123.45 MiB/sec)
    # File I/O test:
    #   reads/s:                      1234.56
    #   writes/s:                     1234.56
    #   fsyncs/s:                     1234.56
    #   read, MiB/s:                  12.34
    #   written, MiB/s:               12.34

    _events_per_second_pattern = re.compile(
        r"events per second:\s+(?P<eps>[\d.]+)", re.M
    )
    _total_time_pattern = re.compile(r"total time:\s+(?P<time>[\d.]+)s", re.M)
    _total_events_pattern = re.compile(
        r"total number of events:\s+(?P<events>\d+)", re.M
    )
    _min_latency_pattern = re.compile(r"min:\s+(?P<min>[\d.]+)", re.M)
    _avg_latency_pattern = re.compile(r"avg:\s+(?P<avg>[\d.]+)", re.M)
    _max_latency_pattern = re.compile(r"max:\s+(?P<max>[\d.]+)", re.M)
    _percentile_95_pattern = re.compile(r"95th percentile:\s+(?P<p95>[\d.]+)", re.M)
    _percentile_99_pattern = re.compile(r"99th percentile:\s+(?P<p99>[\d.]+)", re.M)

    # Memory patterns
    _memory_ops_per_sec_pattern = re.compile(r"(?P<ops>[\d.]+) per second", re.M)
    _memory_throughput_pattern = re.compile(r"(?P<throughput>[\d.]+) MiB/sec", re.M)

    # File I/O patterns
    _fileio_reads_pattern = re.compile(r"reads/s:\s+(?P<reads>[\d.]+)", re.M)
    _fileio_writes_pattern = re.compile(r"writes/s:\s+(?P<writes>[\d.]+)", re.M)
    _fileio_fsyncs_pattern = re.compile(r"fsyncs/s:\s+(?P<fsyncs>[\d.]+)", re.M)
    _fileio_read_throughput_pattern = re.compile(
        r"read, MiB/s:\s+(?P<read_throughput>[\d.]+)", re.M
    )
    _fileio_write_throughput_pattern = re.compile(
        r"written, MiB/s:\s+(?P<write_throughput>[\d.]+)", re.M
    )

    @property
    def command(self) -> str:
        return "sysbench"

    @property
    def can_install(self) -> bool:
        return True

    def install(self) -> bool:
        posix_os: Posix = cast(Posix, self.node.os)
        if not self._check_exists():
            posix_os.install_packages("sysbench")
        return self._check_exists()

    def run_cpu_test(
        self,
        max_prime: int = 20000,
        threads: int = 0,
        time: int = 60,
    ) -> Dict[str, Any]:
        """
        Run CPU performance test using prime number calculation.

        Args:
            max_prime: Maximum prime number to calculate (default: 20000)
            threads: Number of threads (default: 0 = CPU count)
            time: Test duration in seconds (default: 60)

        Returns:
            Dictionary with performance metrics
        """
        if threads == 0:
            from lisa.tools import Lscpu

            lscpu = self.node.tools[Lscpu]
            threads = lscpu.get_core_count()

        cmd = (
            f"cpu --cpu-max-prime={max_prime} " f"--threads={threads} --time={time} run"
        )
        result = self.run(cmd, force_run=True, timeout=time + 30)
        result.assert_exit_code()

        return self._parse_cpu_results(result.stdout)

    def run_memory_test(
        self,
        operation: str = "write",
        total_size: str = "100G",
        threads: int = 0,
        time: int = 60,
    ) -> Dict[str, Any]:
        """
        Run memory performance test.

        Args:
            operation: Type of memory operation (read/write/readwrite)
            total_size: Total size of data to transfer (default: 100G)
            threads: Number of threads (default: 0 = CPU count)
            time: Test duration in seconds (default: 60)

        Returns:
            Dictionary with performance metrics
        """
        if threads == 0:
            from lisa.tools import Lscpu

            lscpu = self.node.tools[Lscpu]
            threads = lscpu.get_core_count()

        cmd = (
            f"memory --memory-oper={operation} "
            f"--memory-total-size={total_size} "
            f"--threads={threads} --time={time} run"
        )
        result = self.run(cmd, force_run=True, timeout=time + 30)
        result.assert_exit_code()

        return self._parse_memory_results(result.stdout)

    def run_fileio_test(
        self,
        test_mode: str = "rndrw",
        file_total_size: str = "2G",
        file_num: int = 16,
        threads: int = 0,
        time: int = 60,
    ) -> Dict[str, Any]:
        """
        Run file I/O performance test.

        Args:
            test_mode: Type of I/O test (seqrd/seqwr/rndrd/rndwr/rndrw)
            file_total_size: Total size of test files (default: 2G)
            file_num: Number of test files (default: 16)
            threads: Number of threads (default: 0 = CPU count)
            time: Test duration in seconds (default: 60)

        Returns:
            Dictionary with performance metrics
        """
        if threads == 0:
            from lisa.tools import Lscpu

            lscpu = self.node.tools[Lscpu]
            threads = lscpu.get_core_count()

        # Prepare test files
        prepare_cmd = (
            f"fileio --file-total-size={file_total_size} "
            f"--file-num={file_num} prepare"
        )
        self._log.debug(f"Preparing fileio test files with command: {prepare_cmd}")
        prepare_result = self.run(prepare_cmd, force_run=True, sudo=True, timeout=300)
        prepare_result.assert_exit_code()

        try:
            # Run test
            run_cmd = (
                f"fileio --file-total-size={file_total_size} "
                f"--file-num={file_num} --file-test-mode={test_mode} "
                f"--threads={threads} --time={time} run"
            )
            self._log.debug(f"Running fileio test with command: {run_cmd}")
            run_result = self.run(run_cmd, force_run=True, sudo=True, timeout=time + 30)
            run_result.assert_exit_code()

            metrics = self._parse_fileio_results(run_result.stdout)
        finally:
            # Clean up test files
            cleanup_cmd = (
                f"fileio --file-total-size={file_total_size} "
                f"--file-num={file_num} cleanup"
            )
            self._log.debug(
                f"Cleaning up fileio test files with command: {cleanup_cmd}"
            )
            cleanup_result = self.run(
                cleanup_cmd, force_run=True, sudo=True, timeout=60
            )
            if cleanup_result.exit_code != 0:
                self._log.warning(
                    f"Failed to cleanup sysbench files: {cleanup_result.stdout}"
                )

        return metrics

    def _parse_cpu_results(self, output: str) -> Dict[str, Any]:
        """Parse CPU test output and extract metrics."""
        metrics: Dict[str, Any] = {}

        # Extract events per second
        eps_match = find_patterns_in_lines(output, [self._events_per_second_pattern])
        if eps_match and eps_match[0]:
            metrics["events_per_second"] = Decimal(eps_match[0][0])

        # Extract total events
        events_match = find_patterns_in_lines(output, [self._total_events_pattern])
        if events_match and events_match[0]:
            metrics["total_events"] = int(events_match[0][0])

        # Extract total time
        time_match = find_patterns_in_lines(output, [self._total_time_pattern])
        if time_match and time_match[0]:
            metrics["total_time_seconds"] = Decimal(time_match[0][0])

        # Extract latency metrics
        min_match = find_patterns_in_lines(output, [self._min_latency_pattern])
        if min_match and min_match[0]:
            metrics["latency_min_ms"] = Decimal(min_match[0][0])

        avg_match = find_patterns_in_lines(output, [self._avg_latency_pattern])
        if avg_match and avg_match[0]:
            metrics["latency_avg_ms"] = Decimal(avg_match[0][0])

        max_match = find_patterns_in_lines(output, [self._max_latency_pattern])
        if max_match and max_match[0]:
            metrics["latency_max_ms"] = Decimal(max_match[0][0])

        p95_match = find_patterns_in_lines(output, [self._percentile_95_pattern])
        if p95_match and p95_match[0]:
            metrics["latency_95th_percentile_ms"] = Decimal(p95_match[0][0])

        p99_match = find_patterns_in_lines(output, [self._percentile_99_pattern])
        if p99_match and p99_match[0]:
            metrics["latency_99th_percentile_ms"] = Decimal(p99_match[0][0])

        return metrics

    def _parse_memory_results(self, output: str) -> Dict[str, Any]:
        """Parse memory test output and extract metrics."""
        metrics: Dict[str, Any] = {}

        # Extract operations per second
        ops_match = find_patterns_in_lines(output, [self._memory_ops_per_sec_pattern])
        if ops_match and ops_match[0]:
            metrics["operations_per_second"] = Decimal(ops_match[0][0])

        # Extract throughput
        throughput_match = find_patterns_in_lines(
            output, [self._memory_throughput_pattern]
        )
        if throughput_match and throughput_match[0]:
            metrics["throughput_mib_per_sec"] = Decimal(throughput_match[0][0])

        # Extract total time
        time_match = find_patterns_in_lines(output, [self._total_time_pattern])
        if time_match and time_match[0]:
            metrics["total_time_seconds"] = Decimal(time_match[0][0])

        # Extract latency metrics
        min_match = find_patterns_in_lines(output, [self._min_latency_pattern])
        if min_match and min_match[0]:
            metrics["latency_min_ms"] = Decimal(min_match[0][0])

        avg_match = find_patterns_in_lines(output, [self._avg_latency_pattern])
        if avg_match and avg_match[0]:
            metrics["latency_avg_ms"] = Decimal(avg_match[0][0])

        max_match = find_patterns_in_lines(output, [self._max_latency_pattern])
        if max_match and max_match[0]:
            metrics["latency_max_ms"] = Decimal(max_match[0][0])

        return metrics

    def _parse_fileio_results(self, output: str) -> Dict[str, Any]:
        """Parse file I/O test output and extract metrics."""
        metrics: Dict[str, Any] = {}

        # Extract IOPS metrics
        reads_match = find_patterns_in_lines(output, [self._fileio_reads_pattern])
        if reads_match and reads_match[0]:
            metrics["reads_per_second"] = Decimal(reads_match[0][0])

        writes_match = find_patterns_in_lines(output, [self._fileio_writes_pattern])
        if writes_match and writes_match[0]:
            metrics["writes_per_second"] = Decimal(writes_match[0][0])

        fsyncs_match = find_patterns_in_lines(output, [self._fileio_fsyncs_pattern])
        if fsyncs_match and fsyncs_match[0]:
            metrics["fsyncs_per_second"] = Decimal(fsyncs_match[0][0])

        # Extract throughput metrics
        read_tp_match = find_patterns_in_lines(
            output, [self._fileio_read_throughput_pattern]
        )
        if read_tp_match and read_tp_match[0]:
            metrics["read_throughput_mib_per_sec"] = Decimal(read_tp_match[0][0])

        write_tp_match = find_patterns_in_lines(
            output, [self._fileio_write_throughput_pattern]
        )
        if write_tp_match and write_tp_match[0]:
            metrics["write_throughput_mib_per_sec"] = Decimal(write_tp_match[0][0])

        # Extract total time
        time_match = find_patterns_in_lines(output, [self._total_time_pattern])
        if time_match and time_match[0]:
            metrics["total_time_seconds"] = Decimal(time_match[0][0])

        # Extract latency metrics
        min_match = find_patterns_in_lines(output, [self._min_latency_pattern])
        if min_match and min_match[0]:
            metrics["latency_min_ms"] = Decimal(min_match[0][0])

        avg_match = find_patterns_in_lines(output, [self._avg_latency_pattern])
        if avg_match and avg_match[0]:
            metrics["latency_avg_ms"] = Decimal(avg_match[0][0])

        max_match = find_patterns_in_lines(output, [self._max_latency_pattern])
        if max_match and max_match[0]:
            metrics["latency_max_ms"] = Decimal(max_match[0][0])

        return metrics
