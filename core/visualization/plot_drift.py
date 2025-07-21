#!/usr/bin/env python3
# ZERO ARCHITECTURE - PRE-DEVELOPMENT BENCHMARKING
# -------------------------------------------------
# THIS IS NOT PRODUCTION CODE - HARDWARE RESEARCH ONLY
#
# MIT License
#
# Copyright (c) 2025 Salik Ridwan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# WARNING: Experimental hardware interactions
# -------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import json

def compute_summary(df, filename):
    duration = df['monotonic'].max() - df['monotonic'].min()
    mean_ppm = df['drift_ppm'].mean()
    stddev_ppm = df['drift_ppm'].std()
    max_drift = df['drift_ppm'].max()
    min_drift = df['drift_ppm'].min()
    # Lag-1 autocorrelation
    if len(df['drift_ppm']) > 1:
        autocorr_lag1 = df['drift_ppm'].autocorr(lag=1)
    else:
        autocorr_lag1 = float('nan')
    summary = {
        "file": os.path.basename(filename),
        "samples": len(df),
        "duration_sec": round(duration, 2),
        "mean_ppm": round(mean_ppm, 2),
        "stddev_ppm": round(stddev_ppm, 2),
        "autocorr_lag1": round(autocorr_lag1, 3) if not pd.isnull(autocorr_lag1) else None,
        "max_drift": round(max_drift, 2),
        "min_drift": round(min_drift, 2)
    }
    return summary

def print_summary_table(summaries):
    if not summaries:
        print("No summaries to display.")
        return
    # Print header
    keys = ["file", "samples", "duration_sec", "mean_ppm", "stddev_ppm", "autocorr_lag1", "max_drift", "min_drift"]
    print("\nSummary Table:")
    print(" | ".join(f"{k:>14}" for k in keys))
    print("-" * (17 * len(keys)))
    for s in summaries:
        print(" | ".join(f"{str(s[k]):>14}" for k in keys))

def analyze_and_plot():
    """Analyze drift logs and create visualizations"""
    # Find the latest log file
    log_files = glob.glob('logs/drift_*.csv')
    if not log_files:
        print("No drift logs found. Run drift_collector first.")
        return
    
    # --- Summarize all logs ---
    summaries = []
    for log in sorted(log_files):
        try:
            df = pd.read_csv(log)
            summary = compute_summary(df, log)
            summaries.append(summary)
        except Exception as e:
            print(f"Could not process {log}: {e}")
    print_summary_table(summaries)
    
    # --- Analyze latest log ---
    latest_log = max(log_files, key=os.path.getctime)
    df = pd.read_csv(latest_log)
    
    print(f"\nAnalyzing: {latest_log}")
    print(f"Total samples: {len(df)}")
    print(f"Time duration: {df['monotonic'].max() - df['monotonic'].min():.2f} seconds")
    
    # Save summary as JSON
    summary = compute_summary(df, latest_log)
    summary_file = latest_log.replace('.csv', '_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to: {summary_file}")
    
    # Create plots
    plt.figure(figsize=(14, 10))
    
    # Drift over time
    plt.subplot(2, 2, 1)
    plt.plot(df['monotonic'], df['drift_ppm'])
    plt.title('Clock Drift Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Drift (PPM)')
    plt.grid(True)
    
    # Drift distribution
    plt.subplot(2, 2, 2)
    plt.hist(df['drift_ppm'], bins=50, alpha=0.7)
    plt.title('Drift Distribution')
    plt.xlabel('Drift (PPM)')
    plt.ylabel('Frequency')
    plt.grid(True)
    
    # Moving statistics
    plt.subplot(2, 2, 3)
    window_size = 100  # 10-second window at 10Hz
    df['rolling_mean'] = df['drift_ppm'].rolling(window_size).mean()
    df['rolling_std'] = df['drift_ppm'].rolling(window_size).std()
    plt.plot(df['monotonic'], df['rolling_mean'], label='Mean')
    plt.plot(df['monotonic'], df['rolling_std'], label='Std Dev')
    plt.title('Moving Statistics')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    
    # Autocorrelation
    plt.subplot(2, 2, 4)
    num_samples = len(df['drift_ppm'])
    maxlags = min(100, num_samples - 1)
    plt.acorr(df['drift_ppm'], maxlags=maxlags, usevlines=False, normed=True)
    plt.title('Drift Autocorrelation')
    plt.xlabel('Lag (samples)')
    plt.ylabel('Correlation')
    plt.grid(True)
    
    plt.tight_layout()
    
    # Save plot
    plot_file = latest_log.replace('.csv', '_analysis.png')
    plt.savefig(plot_file)
    print(f"Analysis saved to: {plot_file}")
    
    # Show plot
    plt.show()

if __name__ == "__main__":
    analyze_and_plot()
