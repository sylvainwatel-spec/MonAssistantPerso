"""
Script to measure application startup time.
This helps verify the impact of lazy loading optimizations.
"""
import time
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("Application Startup Time Measurement")
print("=" * 60)

# Measure import time
start_time = time.time()

# Import main module (this triggers all startup imports)
import main

import_time = time.time() - start_time

print(f"\n✓ Import time: {import_time:.3f} seconds")

# Measure app initialization time
start_init = time.time()
app = main.App()
init_time = time.time() - start_init

print(f"✓ App initialization time: {init_time:.3f} seconds")

total_time = time.time() - start_time
print(f"\n{'=' * 60}")
print(f"TOTAL STARTUP TIME: {total_time:.3f} seconds")
print(f"{'=' * 60}\n")

# Don't actually run the app
app.destroy()

# Exit cleanly
sys.exit(0)
