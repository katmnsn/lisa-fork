# Sysbench Performance Test Suite

## Overview

This test suite uses [sysbench](https://github.com/akopytov/sysbench) to benchmark various aspects of system performance including CPU, memory, thread scheduling, and mutex operations.

## Test Cases

### 1. CPU Performance Test (`perf_sysbench_cpu`)

**Purpose**: Measures CPU performance using prime number calculation.

**What it tests**:
- CPU computational performance
- Single and multi-threaded workloads
- Prime number verification using standard division

**Metrics Reported**:
- `cpu_events_per_second`: Number of CPU events completed per second
- `cpu_latency_avg`: Average latency for CPU operations (ms)
- Additional latency metrics: min, max, 95th percentile

**Typical Use Cases**:
- Baseline CPU performance measurement
- Comparing CPU performance across different VM sizes
- Validating CPU scaling across different instance types

---

### 2. Memory Write Performance Test (`perf_sysbench_memory_write`)

**Purpose**: Measures memory write throughput.

**What it tests**:
- Sequential memory write operations
- Memory bandwidth for write operations
- Multi-threaded memory access patterns

**Metrics Reported**:
- `memory_write_ops_per_second`: Memory write operations per second
- `memory_write_latency_avg`: Average latency for write operations (ms)
- Additional latency metrics: min, max, 95th percentile

**Typical Use Cases**:
- Memory-intensive workload performance testing
- Memory bandwidth validation
- Comparing memory performance across different instance types

---

### 3. Memory Read Performance Test (`perf_sysbench_memory_read`)

**Purpose**: Measures memory read throughput.

**What it tests**:
- Sequential memory read operations
- Memory bandwidth for read operations
- Multi-threaded memory access patterns

**Metrics Reported**:
- `memory_read_ops_per_second`: Memory read operations per second
- `memory_read_latency_avg`: Average latency for read operations (ms)
- Additional latency metrics: min, max, 95th percentile

**Typical Use Cases**:
- Memory-intensive workload performance testing
- Memory bandwidth validation
- Read-heavy workload performance analysis

---

### 4. Thread Scheduling Performance Test (`perf_sysbench_threads`)

**Purpose**: Measures thread scheduling and context switching performance.

**What it tests**:
- Thread scheduling efficiency
- Context switching overhead
- Mutex acquire/release with thread yields
- Thread fairness

**Metrics Reported**:
- `threads_latency_avg`: Average latency for thread operations (ms)
- `threads_fairness_avg`: Thread fairness metric
- `threads_fairness_stddev`: Standard deviation of thread fairness
- Additional latency metrics: min, max, 95th percentile

**Typical Use Cases**:
- Evaluating scheduler performance
- Testing multi-threaded application scenarios
- Validating thread performance across different kernels

---

### 5. Mutex Performance Test (`perf_sysbench_mutex`)

**Purpose**: Measures mutex lock/unlock performance under high contention.

**What it tests**:
- Mutex implementation efficiency
- Lock contention handling
- Multi-threaded synchronization performance

**Metrics Reported**:
- `mutex_latency_avg`: Average latency for mutex operations (ms)
- `mutex_fairness_avg`: Mutex fairness metric
- Additional latency metrics: min, max, 95th percentile

**Typical Use Cases**:
- Testing synchronization primitive performance
- Evaluating performance under high lock contention
- Comparing mutex implementations across different kernels

---

## Running the Tests

### Using LISA Command Line

To run all sysbench tests:

```bash
lisa -r ./runbook.yml -v subscription_id:<your-subscription-id>
```

Example runbook (`runbook.yml`):

```yaml
name: sysbench_performance_tests
test_project: lisa
test_pass: sysbench
environment:
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: Ubuntu
          version: "22.04"
testcase:
  - criteria:
      area: sysbench
      category: performance
```

### Running Individual Tests

To run only CPU tests:

```bash
lisa -r ./runbook.yml -t perf_sysbench_cpu
```

To run only memory tests:

```bash
lisa -r ./runbook.yml -t "perf_sysbench_memory_*"
```

### Test Parameters

The tests automatically scale based on the number of CPU cores available on the test VM:
- CPU test: Uses all available cores
- Memory tests: Uses all available cores for parallel operations
- Thread tests: Creates threads equal to core count
- Mutex tests: Creates threads equal to core count

Default timeout: **7200 seconds (2 hours)**

---

## Understanding Test Results

### Performance Metrics

All tests report performance metrics in the LISA performance message format, which includes:

1. **Primary Metrics**: The main performance indicator (e.g., events/sec, ops/sec)
2. **Latency Metrics**: Response time measurements
   - `latency_min_ms`: Best case latency
   - `latency_avg_ms`: Average latency
   - `latency_max_ms`: Worst case latency
   - `latency_95th_percentile_ms`: 95th percentile latency
3. **Fairness Metrics** (for thread/mutex tests): Distribution of work across threads

### Example Output

```
Sysbench CPU test results: {
  'events_per_second': 1234.56,
  'latency_min_ms': 0.50,
  'latency_avg_ms': 1.23,
  'latency_max_ms': 10.45,
  'latency_95th_percentile_ms': 2.34
}
```

---

## Requirements

### OS Support

- ✅ **Supported**: Linux distributions (Ubuntu, Debian, RHEL, CentOS, SUSE, etc.)
- ❌ **Not Supported**: Windows, BSD

### Package Availability

Sysbench is available in the default package repositories for most major Linux distributions:

- **Ubuntu/Debian**: `apt install sysbench`
- **RHEL/CentOS**: `yum install sysbench`
- **SUSE**: `zypper install sysbench`

### Minimum VM Requirements

- **CPU tests**: 1+ vCPU (2+ recommended)
- **Memory tests**: 2+ GB RAM (4+ GB recommended)
- **Thread/Mutex tests**: 2+ vCPUs (4+ recommended for meaningful results)

---

## Test Implementation Details

### File Structure

```
lisa/
├── tools/
│   └── sysbench.py          # Sysbench tool wrapper
└── microsoft/
    └── testsuites/
        └── performance/
            └── sysbench.py  # Sysbench test suite
```

### Tool Implementation (`lisa/tools/sysbench.py`)

The Sysbench tool wrapper provides:
- Installation support via package managers
- Test execution methods for different benchmark types
- Result parsing with regex patterns
- Latency and performance metric extraction

Key methods:
- `run_cpu_test()`: Execute CPU benchmark
- `run_memory_test()`: Execute memory benchmark
- `run_threads_test()`: Execute thread scheduling benchmark
- `run_mutex_test()`: Execute mutex benchmark
- `parse_*_results()`: Parse benchmark output and extract metrics

### Test Suite Implementation

Each test case follows the LISA pattern:
1. Get the Sysbench tool instance
2. Get CPU count for thread scaling
3. Run the appropriate benchmark
4. Parse results
5. Send performance metrics using `send_unified_perf_message()`

---

## Troubleshooting

### Sysbench Not Available

**Issue**: Sysbench package not found in repositories

**Solution**: 
- For older distributions, you may need to compile from source
- Check if EPEL repository is enabled (for RHEL/CentOS)
- Verify internet connectivity for package installation

### Performance Variations

**Issue**: Results vary significantly between runs

**Possible Causes**:
- CPU throttling or power management
- Background processes consuming resources
- VM noisy neighbor effects
- Network-based storage impacting memory tests

**Recommendations**:
- Run tests multiple times and average results
- Use dedicated VM instances when possible
- Check for background processes with `top` or `htop`
- Consider using VM sizes with guaranteed performance

### Test Timeouts

**Issue**: Tests exceed the 2-hour timeout

**Solution**:
- Reduce `max_time` parameter in test methods
- Use fewer threads for testing
- Check if VM is under-provisioned for the workload

---

## References

- [Sysbench GitHub Repository](https://github.com/akopytov/sysbench)
- [Sysbench Documentation](https://github.com/akopytov/sysbench/tree/master/docs)
- [LISA Framework Documentation](https://github.com/microsoft/lisa/tree/main/docs)

---

## Contributing

To add new sysbench test cases:

1. Add new test method to `Sysbench` tool class in `lisa/tools/sysbench.py`
2. Add corresponding parsing logic if needed
3. Create new test case in `lisa/microsoft/testsuites/performance/sysbench.py`
4. Follow LISA test case patterns for metadata and metrics reporting
5. Update this README with test documentation

---

## License

Copyright (c) Microsoft Corporation.
Licensed under the MIT license.
