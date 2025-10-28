# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Any, Dict

from lisa import Node, TestCaseMetadata, TestSuite, TestSuiteMetadata, notifier
from lisa.messages import (
    SysbenchCPUMessage,
    SysbenchFileIOMessage,
    SysbenchMemoryMessage,
    create_perf_message,
    send_unified_perf_message,
)
from lisa.operating_system import BSD, Windows
from lisa.testsuite import TestResult, simple_requirement
from lisa.tools import Sysbench


@TestSuiteMetadata(
    area="performance",
    category="performance",
    description="""
    This test suite uses sysbench to benchmark CPU, memory, and file I/O performance.
    """,
)
class SysbenchPerformance(TestSuite):
    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure CPU performance via prime number
        calculation benchmark.

        Steps:
        1. Install sysbench tool.
        2. Run CPU benchmark with configurable prime number calculation.
        3. Extract performance metrics (events/sec, latency percentiles).
        4. Send metrics to LISA's unified performance message system.

        The test runs with thread count matching the node's CPU core count.
        """,
        priority=3,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_cpu(
        self,
        node: Node,
        result: TestResult,
    ) -> None:
        sysbench = node.tools[Sysbench]

        # Run CPU test
        metrics = sysbench.run_cpu_test(
            max_prime=20000,
            threads=0,  # 0 = auto-detect CPU count
            time=60,
        )

        # Create and send performance messages
        self._create_and_notify_perf_message(
            SysbenchCPUMessage,
            node,
            result,
            "sysbench_cpu",
            metrics,
        )

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure memory performance with read/write
        operations.

        Steps:
        1. Install sysbench tool.
        2. Run memory benchmark with write operations.
        3. Extract performance metrics (ops/sec, throughput MiB/sec, latency).
        4. Send metrics to LISA's unified performance message system.

        The test transfers 100GB of data with thread count matching the node's
        CPU core count.
        """,
        priority=3,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_memory(
        self,
        node: Node,
        result: TestResult,
    ) -> None:
        sysbench = node.tools[Sysbench]

        # Run memory test
        metrics = sysbench.run_memory_test(
            operation="write",
            total_size="100G",
            threads=0,  # 0 = auto-detect CPU count
            time=60,
        )

        # Create and send performance messages
        self._create_and_notify_perf_message(
            SysbenchMemoryMessage,
            node,
            result,
            "sysbench_memory",
            metrics,
        )

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure file I/O performance with random
        read/write operations.

        Steps:
        1. Install sysbench tool.
        2. Prepare test files (2GB across 16 files).
        3. Run file I/O benchmark with random read/write mode.
        4. Extract performance metrics (IOPS, throughput, latency).
        5. Clean up test files.
        6. Send metrics to LISA's unified performance message system.

        The test runs with thread count matching the node's CPU core count.
        """,
        priority=3,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def sysbench_fileio(
        self,
        node: Node,
        result: TestResult,
    ) -> None:
        sysbench = node.tools[Sysbench]

        # Run file I/O test
        metrics = sysbench.run_fileio_test(
            test_mode="rndrw",  # random read/write
            file_total_size="2G",
            file_num=16,
            threads=0,  # 0 = auto-detect CPU count
            time=60,
        )

        # Create and send performance messages
        self._create_and_notify_perf_message(
            SysbenchFileIOMessage,
            node,
            result,
            "sysbench_fileio",
            metrics,
        )

    def _create_and_notify_perf_message(
        self,
        message_type: type,
        node: Node,
        result: TestResult,
        test_case_name: str,
        metrics: Dict[str, Any],
    ) -> None:
        """
        Create and send performance messages for sysbench test results.

        Args:
            message_type: The message class type (e.g., SysbenchCPUMessage)
            node: The test node
            result: The test result object
            test_case_name: Name of the test case
            metrics: Dictionary of performance metrics
        """
        tool = "sysbench"
        other_fields: Dict[str, Any] = metrics.copy()
        other_fields["tool"] = tool

        # Create typed performance message
        message = create_perf_message(  # type: ignore
            message_type,
            node,
            result,
            test_case_name,
            other_fields,
        )
        notifier.notify(message)

        # Send unified performance messages for each metric
        for key, value in metrics.items():
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name=test_case_name,
                tool=tool,
                metric_name=key,
                metric_value=value,
            )
