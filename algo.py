import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import random
import sys
import csv
import os
import statistics  
sys.setrecursionlimit(3000)

RUNS = 5


# --- 1. The Algorithms ---

# 1) Iterative
def find_max_iterative(data):
    current_max = data[0]
    for num in data[1:]:
        if num > current_max:
            current_max = num
    return current_max

# 2) Recursive
def find_max_recursive(data, idx=1, current_max=None):
    if current_max is None:
        current_max = data[0]
    if idx >= len(data):
        return current_max
    if data[idx] > current_max:
        current_max = data[idx]
    return find_max_recursive(data, idx + 1, current_max)


# --- 2. UI Logic ---

def generate_random_numbers():
    size = random.randint(10, 500)
    random_list = [str(random.randint(1, 10000)) for _ in range(size)]
    text_data = ", ".join(random_list)
    entry_input.delete(0, tk.END)
    entry_input.insert(0, text_data)
    lbl_winner.config(text="Data Generated! Press Start.", fg="black")


def get_numbers():
    raw_text = entry_input.get()
    try:
        str_list = raw_text.split(',')
        num_list = [int(x.strip()) for x in str_list if x.strip()]
        if not num_list:
            messagebox.showerror("Error", "Please enter at least one number.")
            return None
        return num_list
    except ValueError:
        messagebox.showerror("Error", "Invalid input! Use numbers separated by commas.")
        return None


def run_comparison():
    data = get_numbers()
    if not data:
        return

    # 1) Iterative: run 5x -> median
    iter_times = []
    res_i = None
    for _ in range(RUNS):
        start_i = time.perf_counter_ns()
        res_i = find_max_iterative(data)
        end_i = time.perf_counter_ns()
        iter_times.append(end_i - start_i)
    time_i = int(statistics.median(iter_times))

    # 2) Recursive: run 5x -> median
    try:
        recur_times = []
        res_r = None
        for _ in range(RUNS):
            start_r = time.perf_counter_ns()
            res_r = find_max_recursive(data)
            end_r = time.perf_counter_ns()
            recur_times.append(end_r - start_r)
        time_r = int(statistics.median(recur_times))

        # Determine Winner
        if time_i < time_r:
            winner = "Iterative"
            lbl_winner.config(text=f"Iterative is Faster! (median of {RUNS})", fg="blue")
        else:
            winner = "Recursive"
            lbl_winner.config(text=f"Recursive is Faster! (median of {RUNS})", fg="green")

    except RecursionError:
        res_r = "Error"
        time_r = 0
        winner = "Failed"
        lbl_winner.config(text="Recursive Failed (RecursionError)", fg="red")

    # 3) Update results
    lbl_iter_res.config(text=str(res_i))
    lbl_iter_time.config(text=f"{time_i} ns (median/{RUNS})")
    lbl_recur_res.config(text=str(res_r))
    lbl_recur_time.config(text=f"{time_r} ns (median/{RUNS})")

    # 4) Add to log
    tree.insert("", tk.END, values=(len(data), f"{time_i}", f"{time_r}", winner))

    btn_export.config(state=tk.NORMAL, bg="#2196F3")


def export_to_csv():
    filename = "experiment_log.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Input Size",
            f"Iterative Median Time (ns) over {RUNS}",
            f"Recursive Median Time (ns) over {RUNS}",
            "Winner"
        ])
        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            writer.writerow(row)

    messagebox.showinfo("Success", f"Log saved to '{filename}'")


# --- 3. GUI ---

root = tk.Tk()
root.title(f"Algorithm Efficiency Project")
root.geometry("650x600")

tk.Label(root, text="Iterative vs Recursive Comparison", font=("Poppins", 14, "bold")).pack(pady=10)

# Section: Input
frame_input = tk.Frame(root)
frame_input.pack(pady=5)
tk.Label(frame_input, text="Input Numbers:").pack(anchor="w")
entry_input = tk.Entry(frame_input, width=70)
entry_input.pack()
entry_input.insert(0, "10, 5, 100, 2, 8")

# Section: Buttons
frame_btns = tk.Frame(root)
frame_btns.pack(pady=10)

btn_gen = tk.Button(frame_btns, text="Random Data (<500)", command=generate_random_numbers, bg="#FFEB3B")
btn_gen.pack(side=tk.LEFT, padx=5)

btn_run = tk.Button(
    frame_btns, text="▶ Run Comparison", command=run_comparison,
    bg="#4CAF50", fg="white", font=("Arial", 10, "bold")
)
btn_run.pack(side=tk.LEFT, padx=5)

btn_export = tk.Button(
    frame_btns, text="💾 Export Log to CSV", command=export_to_csv,
    state=tk.DISABLED, bg="#dddddd", fg="white"
)
btn_export.pack(side=tk.LEFT, padx=5)

# Section: Current Result
frame_res = tk.LabelFrame(root, text=f"Current Run Results (Median of {RUNS} runs)", padx=10, pady=5)
frame_res.pack(fill="x", padx=20, pady=5)

tk.Label(frame_res, text="Iterative Time:", font=("Arial", 10, "bold"), fg="blue").grid(row=0, column=0, padx=10)
lbl_iter_time = tk.Label(frame_res, text="-")
lbl_iter_time.grid(row=0, column=1)

tk.Label(frame_res, text="Recursive Time:", font=("Arial", 10, "bold"), fg="green").grid(row=0, column=2, padx=10)
lbl_recur_time = tk.Label(frame_res, text="-")
lbl_recur_time.grid(row=0, column=3)

# Hidden helper labels
lbl_iter_res = tk.Label(root)
lbl_recur_res = tk.Label(root)

lbl_winner = tk.Label(root, text="", font=("Arial", 11, "bold"))
lbl_winner.pack(pady=5)

# Section: History Log
tk.Label(root, text="--- Experiment History Log ---", font=("Arial", 10, "bold")).pack(pady=(10, 0))

cols = ("Size", "Iterative(ns)", "Recursive(ns)", "Winner")
tree = ttk.Treeview(root, columns=cols, show="headings", height=8)

tree.heading("Size", text="Input Size")
tree.heading("Iterative(ns)", text="Iterative Median (ns)")
tree.heading("Recursive(ns)", text="Recursive Median (ns)")
tree.heading("Winner", text="Winner")

tree.column("Size", width=90, anchor="center")
tree.column("Iterative(ns)", width=170, anchor="center")
tree.column("Recursive(ns)", width=170, anchor="center")
tree.column("Winner", width=100, anchor="center")

tree.pack(fill="x", padx=20, pady=10)

print("Saving files to:", os.getcwd())

root.mainloop()
