# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Any, Dict

from lisa import Logger, Node, TestCaseMetadata, TestSuite, TestSuiteMetadata
from lisa.messages import create_perf_message, send_unified_perf_message
from lisa.operating_system import BSD, Windows
from lisa.testsuite import TestResult, simple_requirement
from lisa.tools import Lscpu, Sysbench
from lisa.util import constants


@TestSuiteMetadata(
    area="sysbench",
    category="performance",
    description="""
    This test suite uses sysbench to benchmark system performance.
    Sysbench is a scriptable multi-threaded benchmark tool that can evaluate
    OS parameters important for databases and other workloads.
    
    The suite includes tests for:
    - CPU performance (prime number calculation)
    - Memory throughput (sequential read/write)
    - Thread scheduling performance
    - Mutex performance
    """,
)
class SysbenchPerformance(TestSuite):
    TIME_OUT = 7200

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure CPU performance.
        
        The CPU test verifies prime numbers by doing standard division of the number by
        all numbers between 2 and the square root of the number. Once a number gives
        a remainder of 0, the next number is calculated.
        
        Steps:
            1. Install sysbench
            2. Run CPU benchmark with prime number calculation
            3. Parse and report performance metrics including events/sec and latency
        """,
        priority=3,
        timeout=TIME_OUT,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def perf_sysbench_cpu(
        self,
        node: Node,
        result: TestResult,
        log: Logger,
    ) -> None:
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]

        # Get number of CPU cores for optimal thread count
        cpu_count = lscpu.get_core_count()

        # Run CPU benchmark
        output = sysbench.run_cpu_test(
            max_prime=20000,
            num_threads=cpu_count,
            max_time=60,
        )

        # Parse results
        metrics = sysbench.parse_cpu_results(output)

        # Log results
        log.info(f"Sysbench CPU test results: {metrics}")

        # Send performance metrics
        if "events_per_second" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_cpu",
                metric_name="cpu_events_per_second",
                metric_value=metrics["events_per_second"],
                metric_unit="events/sec",
                metric_description="CPU events per second (prime number calculation)",
                tool="sysbench",
            )

        # Send latency metrics
        if "latency_avg_ms" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_cpu",
                metric_name="cpu_latency_avg",
                metric_value=metrics["latency_avg_ms"],
                metric_unit="ms",
                metric_description="Average latency for CPU operations",
                tool="sysbench",
            )

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure memory write throughput.
        
        The memory test allocates a memory buffer and performs sequential write
        operations on it until either the total number of operations reaches
        the specified limit or the time limit is exceeded.
        
        Steps:
            1. Install sysbench
            2. Run memory write benchmark
            3. Parse and report memory throughput and latency metrics
        """,
        priority=3,
        timeout=TIME_OUT,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def perf_sysbench_memory_write(
        self,
        node: Node,
        result: TestResult,
        log: Logger,
    ) -> None:
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]

        # Get number of CPU cores for optimal thread count
        cpu_count = lscpu.get_core_count()

        # Run memory write benchmark
        output = sysbench.run_memory_test(
            memory_block_size="1K",
            memory_total_size="100G",
            num_threads=cpu_count,
            max_time=60,
            memory_oper="write",
        )

        # Parse results
        metrics = sysbench.parse_memory_results(output)

        # Log results
        log.info(f"Sysbench memory write test results: {metrics}")

        # Send performance metrics
        if "operations_per_second" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_memory_write",
                metric_name="memory_write_ops_per_second",
                metric_value=metrics["operations_per_second"],
                metric_unit="ops/sec",
                metric_description="Memory write operations per second",
                tool="sysbench",
            )

        # Send latency metrics
        if "latency_avg_ms" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_memory_write",
                metric_name="memory_write_latency_avg",
                metric_value=metrics["latency_avg_ms"],
                metric_unit="ms",
                metric_description="Average latency for memory write operations",
                tool="sysbench",
            )

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure memory read throughput.
        
        The memory test allocates a memory buffer and performs sequential read
        operations on it until either the total number of operations reaches
        the specified limit or the time limit is exceeded.
        
        Steps:
            1. Install sysbench
            2. Run memory read benchmark
            3. Parse and report memory throughput and latency metrics
        """,
        priority=3,
        timeout=TIME_OUT,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def perf_sysbench_memory_read(
        self,
        node: Node,
        result: TestResult,
        log: Logger,
    ) -> None:
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]

        # Get number of CPU cores for optimal thread count
        cpu_count = lscpu.get_core_count()

        # Run memory read benchmark
        output = sysbench.run_memory_test(
            memory_block_size="1K",
            memory_total_size="100G",
            num_threads=cpu_count,
            max_time=60,
            memory_oper="read",
        )

        # Parse results
        metrics = sysbench.parse_memory_results(output)

        # Log results
        log.info(f"Sysbench memory read test results: {metrics}")

        # Send performance metrics
        if "operations_per_second" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_memory_read",
                metric_name="memory_read_ops_per_second",
                metric_value=metrics["operations_per_second"],
                metric_unit="ops/sec",
                metric_description="Memory read operations per second",
                tool="sysbench",
            )

        # Send latency metrics
        if "latency_avg_ms" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_memory_read",
                metric_name="memory_read_latency_avg",
                metric_value=metrics["latency_avg_ms"],
                metric_unit="ms",
                metric_description="Average latency for memory read operations",
                tool="sysbench",
            )

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure thread scheduling performance.
        
        The threads test creates a specified number of threads and each thread
        acquires a mutex, then yields, repeating this operation a specified
        number of times. This test is useful for evaluating the scheduler
        performance and mutex implementation efficiency.
        
        Steps:
            1. Install sysbench
            2. Run threads scheduling benchmark
            3. Parse and report scheduling metrics including latency and fairness
        """,
        priority=3,
        timeout=TIME_OUT,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def perf_sysbench_threads(
        self,
        node: Node,
        result: TestResult,
        log: Logger,
    ) -> None:
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]

        # Get number of CPU cores for thread count
        cpu_count = lscpu.get_core_count()

        # Run threads benchmark
        output = sysbench.run_threads_test(
            num_threads=cpu_count,
            thread_yields=100,
            thread_locks=2,
            max_time=60,
        )

        # Parse results
        metrics = sysbench.parse_threads_results(output)

        # Log results
        log.info(f"Sysbench threads test results: {metrics}")

        # Send latency metrics
        if "latency_avg_ms" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_threads",
                metric_name="threads_latency_avg",
                metric_value=metrics["latency_avg_ms"],
                metric_unit="ms",
                metric_description="Average latency for thread scheduling operations",
                tool="sysbench",
            )

        # Send fairness metrics
        if "threads_fairness_avg" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_threads",
                metric_name="threads_fairness_avg",
                metric_value=metrics["threads_fairness_avg"],
                metric_unit="count",
                metric_description="Thread fairness average",
                tool="sysbench",
            )

    @TestCaseMetadata(
        description="""
        This test case uses sysbench to measure mutex performance.
        
        The mutex test creates a specified number of mutexes and locks each of them
        a specified number of times. All threads are pounding the same mutex and
        there is no random distribution involved. This test is useful for evaluating
        mutex implementation efficiency under high contention.
        
        Steps:
            1. Install sysbench
            2. Run mutex performance benchmark
            3. Parse and report mutex operation metrics including latency
        """,
        priority=3,
        timeout=TIME_OUT,
        requirement=simple_requirement(
            unsupported_os=[BSD, Windows],
        ),
    )
    def perf_sysbench_mutex(
        self,
        node: Node,
        result: TestResult,
        log: Logger,
    ) -> None:
        sysbench = node.tools[Sysbench]
        lscpu = node.tools[Lscpu]

        # Get number of CPU cores for thread count
        cpu_count = lscpu.get_core_count()

        # Run mutex benchmark
        output = sysbench.run_mutex_test(
            num_threads=cpu_count,
            mutex_num=4096,
            mutex_locks=50000,
            mutex_loops=10000,
        )

        # Parse results - mutex test has similar output to threads test
        metrics = sysbench.parse_threads_results(output)

        # Log results
        log.info(f"Sysbench mutex test results: {metrics}")

        # Send latency metrics
        if "latency_avg_ms" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_mutex",
                metric_name="mutex_latency_avg",
                metric_value=metrics["latency_avg_ms"],
                metric_unit="ms",
                metric_description="Average latency for mutex operations",
                tool="sysbench",
            )

        # Send fairness metrics if available
        if "threads_fairness_avg" in metrics:
            send_unified_perf_message(
                node=node,
                test_result=result,
                test_case_name="perf_sysbench_mutex",
                metric_name="mutex_fairness_avg",
                metric_value=metrics["threads_fairness_avg"],
                metric_unit="count",
                metric_description="Mutex fairness average",
                tool="sysbench",
            )
