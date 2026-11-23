"""
Publication-Quality Figure Generator using Matplotlib.
Generates comparative graphs for the research paper.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_charts():
    results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    csv_path = os.path.join(results_dir, "benchmark_results.csv")
    
    if not os.path.exists(csv_path):
        print("Results CSV not found. Run run_benchmark.py first.")
        return
        
    df = pd.read_csv(csv_path)
    
    # 1. Answer Leakage Rate Comparison by Subject
    subjects = df["subject"].unique()
    baseline_leakages = [df[df["subject"] == s]["baseline_leakage"].mean() * 100 for s in subjects]
    socratic_leakages = [df[df["subject"] == s]["socratic_leakage"].mean() * 100 for s in subjects]
    
    x = np.arange(len(subjects))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, baseline_leakages, width, label="Baseline (Unconstrained LLM)", color="#d9534f")
    rects2 = ax.bar(x + width/2, socratic_leakages, width, label="SocraticGuard (Intervention)", color="#28a745")
    
    ax.set_ylabel("Answer Leakage Rate (%)", fontsize=12)
    ax.set_title("Direct Answer Leakage by Subject Domain", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(subjects, fontsize=11)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    chart1_path = os.path.join(results_dir, "leakage_comparison.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved: {chart1_path}")
    
    # 2. Bloom's Taxonomy Cognitive Demand Comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Overall", "Mathematics", "Computer Science", "Physics"]
    
    base_blooms = [df["baseline_blooms"].mean()] + [df[df["subject"] == s]["baseline_blooms"].mean() for s in subjects]
    soc_blooms = [df["socratic_blooms"].mean()] + [df[df["subject"] == s]["socratic_blooms"].mean() for s in subjects]
    
    x_b = np.arange(len(categories))
    ax.bar(x_b - width/2, base_blooms, width, label="Baseline LLM", color="#f0ad4e")
    ax.bar(x_b + width/2, soc_blooms, width, label="SocraticGuard", color="#0275d8")
    
    ax.set_ylabel("Bloom's Revised Taxonomy Level (1 - 6)", fontsize=12)
    ax.set_title("Cognitive Demand Level Elicited by Pedagogical Scaffold", fontsize=14, fontweight="bold")
    ax.set_xticks(x_b)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 6.5)
    ax.legend(fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    chart2_path = os.path.join(results_dir, "blooms_taxonomy_distribution.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved: {chart2_path}")

if __name__ == "__main__":
    generate_charts()
