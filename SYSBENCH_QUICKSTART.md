# Quick Start: Sysbench Performance Tests

## Prerequisites

1. **LISA installed and configured**
   ```bash
   cd /path/to/lisa
   python -m pip install --editable .[azure,libvirt]
   ```

2. **Azure credentials configured**
   - Service Principal or Azure CLI authentication
   - Valid Azure subscription

## Running Tests - 3 Simple Steps

### Step 1: Create a Minimal Runbook

Create `my_sysbench_test.yml`:

```yaml
name: sysbench_test
environment:
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: Ubuntu
          version: "22.04"
testcase:
  - criteria:
      area: sysbench
```

### Step 2: Run the Tests

```bash
# Run all sysbench tests
lisa -r my_sysbench_test.yml -v subscription_id:YOUR_SUBSCRIPTION_ID

# Or run a specific test
lisa -r my_sysbench_test.yml -t perf_sysbench_cpu -v subscription_id:YOUR_SUBSCRIPTION_ID
```

### Step 3: View Results

Results are saved in `./lisa/runtime/` directory:
- Console output shows real-time progress
- HTML report in `./lisa/runtime/lisa-<timestamp>.html`
- Logs in `./lisa/runtime/log/`

## Test Selection Examples

### Run CPU Test Only
```bash
lisa -r my_sysbench_test.yml -t perf_sysbench_cpu
```

### Run All Memory Tests
```bash
lisa -r my_sysbench_test.yml -t "perf_sysbench_memory_*"
```

### Run Thread and Mutex Tests
```bash
lisa -r my_sysbench_test.yml -t perf_sysbench_threads,perf_sysbench_mutex
```

## Understanding Results

Each test outputs metrics like:

```
Sysbench CPU test results: {
  'events_per_second': 1234.56,      # Higher is better
  'latency_avg_ms': 1.23,            # Lower is better
  'latency_95th_percentile_ms': 2.34 # Lower is better
}
```

## Common Use Cases

### 1. Baseline Performance Test
Test a single VM to establish baseline:
```yaml
name: baseline_test
environment:
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: Ubuntu
          version: "22.04"
testcase:
  - criteria:
      area: sysbench
```

### 2. Compare VM Sizes
Test across multiple VM sizes:
```yaml
name: vm_size_comparison
environment:
  # 2 vCPU
  - nodes:
      - type: Standard_D2s_v5
        os:
          type: Ubuntu
          version: "22.04"
  # 4 vCPU
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: Ubuntu
          version: "22.04"
  # 8 vCPU
  - nodes:
      - type: Standard_D8s_v5
        os:
          type: Ubuntu
          version: "22.04"
testcase:
  - criteria:
      area: sysbench
```

### 3. Cross-Distribution Testing
Test across different OS distributions:
```yaml
name: distro_comparison
environment:
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: Ubuntu
          version: "22.04"
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: Debian
          version: "12"
  - nodes:
      - type: Standard_D4s_v5
        os:
          type: RHEL
          version: "9"
testcase:
  - criteria:
      area: sysbench
```

## Troubleshooting

### Issue: "sysbench command not found"
**Solution**: The test automatically installs sysbench. If it fails, check:
- VM has internet connectivity
- Package repositories are accessible
- Sufficient disk space

### Issue: Test takes too long
**Solution**: Default timeout is 2 hours. Reduce test time:
- Modify `max_time` parameter in test methods
- Run fewer tests using `-t` flag
- Use smaller VM sizes for faster execution

### Issue: Results vary between runs
**Solution**: Performance can vary due to:
- Azure VM noisy neighbors
- CPU throttling
- Background processes

**Recommendation**: Run tests multiple times and average results.

## Advanced Configuration

### Custom Test Parameters

To customize test parameters, modify the test suite code:

```python
# In lisa/microsoft/testsuites/performance/sysbench.py
output = sysbench.run_cpu_test(
    max_prime=20000,      # Increase for longer/harder test
    num_threads=cpu_count, # Or set fixed number
    max_time=60,          # Test duration in seconds
)
```

### Enable Performance Database

Add to your runbook to store results in a database:

```yaml
notifier:
  - type: html
    path: ./results.html
  # Add your database notifier here
```

## What Each Test Measures

| Test | What It Measures | Good For |
|------|------------------|----------|
| `perf_sysbench_cpu` | CPU computational power | CPU-intensive workloads |
| `perf_sysbench_memory_write` | Memory write bandwidth | Write-heavy applications |
| `perf_sysbench_memory_read` | Memory read bandwidth | Read-heavy applications |
| `perf_sysbench_threads` | Thread scheduling efficiency | Multi-threaded apps |
| `perf_sysbench_mutex` | Lock contention handling | High-concurrency apps |

## Next Steps

1. **Run basic test** to verify setup
2. **Review results** in HTML report
3. **Customize runbook** for your needs
4. **Set up trending** to track performance over time
5. **Integrate with CI/CD** for automated testing

## Getting Help

- **LISA Documentation**: https://github.com/microsoft/lisa
- **Sysbench Documentation**: https://github.com/akopytov/sysbench
- **Detailed README**: See `lisa/microsoft/testsuites/performance/sysbench_README.md`

## Example Commands Cheat Sheet

```bash
# List all sysbench tests
lisa -l | grep sysbench

# Dry run to see what would execute
lisa -r my_sysbench_test.yml --dry-run

# Run with debug logging
lisa -r my_sysbench_test.yml --log-level DEBUG

# Run and keep VMs for debugging
lisa -r my_sysbench_test.yml --no-cleanup

# Run with specific subscription
lisa -r my_sysbench_test.yml -v subscription_id:12345678-1234-1234-1234-123456789abc
```

Happy Testing! 🚀
