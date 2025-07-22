import matplotlib.pyplot as plt

def plot_gantt(schedule):
    lanes = {"LaserCutter": 0, "CNC_Mill": 1, "PaintStation": 2}
    colors = {"Job1": "skyblue", "Job2": "lightgreen", "Job3": "salmon"}
    fig, ax = plt.subplots(figsize=(10, 4))

    for job, task, machine, start, end in schedule:
        ax.barh(lanes[machine], end - start, left=start, height=0.4,
                color=colors.get(job, "gray"), edgecolor='black')
        ax.text((start + end) / 2, lanes[machine], f"{job}-{task}",
                ha='center', va='center', fontsize=8)

    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["LaserCutter", "CNC Mill", "PaintStation"])
    ax.set_xlabel("Time (minutes)")
    ax.set_title("Factory Gantt Chart")
    ax.grid(True)
    plt.tight_layout()
    plt.show()
