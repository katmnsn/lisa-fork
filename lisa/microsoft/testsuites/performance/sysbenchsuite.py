# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
from typing import Any, Dict

from lisa import Logger, Node, TestCaseMetadata, TestSuite, TestSuiteMetadata
from lisa.operating_system import BSD, Windows
from lisa.testsuite import TestResult, simple_requirement
from lisa.tools import Lscpu, Sysbench


@TestSuiteMetadata(
    area="sysbench",
    category="performance",
    description="""
    This test suite validates system performance using the sysbench benchmark tool.
    Tests cover CPU, memory, thread scheduler, and file I/O performance.
    """,
)
class SysbenchSuite(TestSuite):
    @TestCaseMetadata(
        description="""
        This test case measures CPU performance using sysbench's prime number
        calculation benchmark. It runs with varying thread counts to test
        single-core and multi-core performance.

        Steps:
        1. Install sysbench if not present
        2. Run CPU test with 1 thread (single-core)
        3. Run CPU test with all available threads (multi-core)
        4. Report events per second for both configurations
        """,
        priority=3,
        requirement=simple_requirement(
            min_count=1,
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_cpu(self, node: Node, log: Logger, result: TestResult) -> None:
        """Test CPU performance with prime number calculation."""
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]
        thread_count = lscpu.get_thread_count()

        log.info("Testing single-core CPU performance")
        single_core_metrics = sysbench.run_cpu_test(
            max_prime=20000,
            threads=1,
            time=10,
        )

        log.info(f"Testing multi-core CPU performance with {thread_count} threads")
        multi_core_metrics = sysbench.run_cpu_test(
            max_prime=20000,
            threads=thread_count,
            time=10,
        )

        # Report metrics
        self._report_metrics(
            result,
            "sysbench_cpu_single_core",
            {
                "tool": "sysbench",
                "test_type": "cpu",
                "threads": 1,
                **single_core_metrics,
            },
        )

        self._report_metrics(
            result,
            "sysbench_cpu_multi_core",
            {
                "tool": "sysbench",
                "test_type": "cpu",
                "threads": thread_count,
                **multi_core_metrics,
            },
        )

        log.info(
            f"CPU performance - Single core: {single_core_metrics['events_per_sec']:.2f} "
            f"events/sec, Multi-core ({thread_count} threads): "
            f"{multi_core_metrics['events_per_sec']:.2f} events/sec"
        )

    @TestCaseMetadata(
        description="""
        This test case measures memory performance using sysbench with different
        access patterns and operations.

        Steps:
        1. Install sysbench if not present
        2. Test sequential write performance
        3. Test sequential read performance
        4. Test random write performance
        5. Test random read performance
        6. Report throughput and operations per second for each pattern
        """,
        priority=3,
        requirement=simple_requirement(
            min_count=1,
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_memory(self, node: Node, log: Logger, result: TestResult) -> None:
        """Test memory performance with various access patterns."""
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]
        thread_count = lscpu.get_thread_count()

        test_configs = [
            ("seq_write", "seq", "write"),
            ("seq_read", "seq", "read"),
            ("rnd_write", "rnd", "write"),
            ("rnd_read", "rnd", "read"),
        ]

        for test_name, access_mode, operation in test_configs:
            log.info(
                f"Testing memory performance: {access_mode} {operation} "
                f"with {thread_count} threads"
            )
            metrics = sysbench.run_memory_test(
                block_size="1K",
                total_size="10G",
                threads=thread_count,
                time=10,
                access_mode=access_mode,
                operation=operation,
            )

            self._report_metrics(
                result,
                f"sysbench_memory_{test_name}",
                {
                    "tool": "sysbench",
                    "test_type": "memory",
                    "access_mode": access_mode,
                    "operation": operation,
                    "threads": thread_count,
                    **metrics,
                },
            )

            log.info(
                f"Memory {access_mode} {operation}: "
                f"{metrics['throughput_mib_sec']:.2f} MiB/s, "
                f"{metrics['ops_per_sec']:.2f} ops/sec"
            )

    @TestCaseMetadata(
        description="""
        This test case measures thread scheduler performance using sysbench's
        thread contention test with mutex locks.

        Steps:
        1. Install sysbench if not present
        2. Run thread test with varying thread counts
        3. Measure lock contention and context switching overhead
        4. Report events per second
        """,
        priority=3,
        requirement=simple_requirement(
            min_count=1,
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_threads(self, node: Node, log: Logger, result: TestResult) -> None:
        """Test thread scheduler performance with mutex locks."""
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]
        thread_count = lscpu.get_thread_count()

        # Test with different thread counts to measure scaling
        test_threads = [4, thread_count] if thread_count > 4 else [thread_count]

        for threads in test_threads:
            log.info(f"Testing thread scheduler performance with {threads} threads")
            metrics = sysbench.run_threads_test(
                threads=threads,
                time=10,
                yields=100,
                locks=8,
            )

            self._report_metrics(
                result,
                f"sysbench_threads_{threads}",
                {
                    "tool": "sysbench",
                    "test_type": "threads",
                    "threads": threads,
                    **metrics,
                },
            )

            log.info(
                f"Thread performance ({threads} threads): "
                f"{metrics['events_per_sec']:.2f} events/sec"
            )

    @TestCaseMetadata(
        description="""
        This test case measures file I/O performance using sysbench with
        various access patterns.

        Steps:
        1. Install sysbench if not present
        2. Test sequential write performance
        3. Test sequential read performance
        4. Test random read/write performance
        5. Report throughput and latency for each pattern
        6. Clean up test files
        """,
        priority=3,
        requirement=simple_requirement(
            min_count=1,
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_fileio(self, node: Node, log: Logger, result: TestResult) -> None:
        """Test file I/O performance with various access patterns."""
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]
        thread_count = lscpu.get_thread_count()

        test_modes = [
            ("seqwr", "Sequential Write"),
            ("seqrd", "Sequential Read"),
            ("rndrw", "Random Read/Write"),
        ]

        for mode, description in test_modes:
            log.info(
                f"Testing file I/O performance: {description} "
                f"with {thread_count} threads"
            )
            metrics = sysbench.run_fileio_test(
                file_test_mode=mode,
                file_total_size="2G",
                file_num=128,
                threads=thread_count,
                time=30,
            )

            self._report_metrics(
                result,
                f"sysbench_fileio_{mode}",
                {
                    "tool": "sysbench",
                    "test_type": "fileio",
                    "mode": mode,
                    "threads": thread_count,
                    **metrics,
                },
            )

            # Build log message based on available metrics
            log_parts = [f"File I/O {description}:"]
            if "read_mib_sec" in metrics:
                log_parts.append(f"read {metrics['read_mib_sec']:.2f} MiB/s")
            if "write_mib_sec" in metrics:
                log_parts.append(f"write {metrics['write_mib_sec']:.2f} MiB/s")
            if "latency_avg_ms" in metrics:
                log_parts.append(f"avg latency {metrics['latency_avg_ms']:.2f} ms")

            log.info(", ".join(log_parts))

    def _report_metrics(
        self,
        result: TestResult,
        test_name: str,
        metrics: Dict[str, Any],
    ) -> None:
        """
        Report performance metrics for a test case.

        Args:
            result: Test result object
            test_name: Name of the specific test
            metrics: Dictionary of metrics to report
        """
        # Log all metrics for debugging
        result.information[test_name] = metrics
