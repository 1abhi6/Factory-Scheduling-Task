import matplotlib.pyplot as plt
from pyomo.environ import *

# Config
machines = ['LaserCutter', 'CNC_Mill', 'PaintStation']


# Data Loader
calendar = {
    'LaserCutter': list(range(480, 1020)),     # 8 AM to 5 PM
    'CNC_Mill': list(range(480, 960)),         # 8 AM to 4 PM
    'PaintStation': list(range(540, 1080))     # 9 AM to 6 PM
}

# Jobs with tasks (job_id, task_id, machine, duration_in_mins, predecessor_task_id)

tasks = [
    ('Job1', 'Cutting', 'LaserCutter', 180, None),
    ('Job1', 'Milling', 'CNC_Mill', 120, 'Cutting'),
    ('Job1', 'Painting', 'PaintStation', 60, 'Milling'),

    ('Job2', 'Cutting', 'LaserCutter', 120, None),
    ('Job2', 'Painting', 'PaintStation', 60, 'Cutting'),

    ('Job3', 'Milling', 'CNC_Mill', 240, None),
    ('Job3', 'Painting', 'PaintStation', 120, 'Milling'),
]

# Model Builder
model = ConcreteModel()

# Sets
model.TASKS = RangeSet(0, len(tasks)-1)
model.MACHINES = Set(initialize=machines)

# Map task index to data
task_dict = {i: t for i, t in enumerate(tasks)}

# Variables
model.start = Var(model.TASKS, domain=NonNegativeReals)
model.end = Var(model.TASKS, domain=NonNegativeReals)
model.makespan = Var(domain=NonNegativeReals)

# Constraints
def duration_rule(m, i):
    return m.end[i] == m.start[i] + task_dict[i][3]

model.task_duration = Constraint(model.TASKS, rule=duration_rule)

# Precedence constraints
def precedence_rule(m, i):
    pred = task_dict[i][4]
    if pred is None:
        return Constraint.Skip
    job = task_dict[i][0]
    for j in model.TASKS:
        if task_dict[j][0] == job and task_dict[j][1] == pred:
            return m.start[i] >= m.end[j]
    return Constraint.Skip

model.precedence = Constraint(model.TASKS, rule=precedence_rule)

# No overlap on same machine
def no_overlap_rule(m, i, j):
    if i >= j:
        return Constraint.Skip
    if task_dict[i][2] != task_dict[j][2]:
        return Constraint.Skip
    return inequality(
        m.end[i] <= m.start[j] + (1 - binary[i, j]) * 1e5,
        m.start[i] >= m.end[j] + binary[i, j] * 1e5
    )
    
model.no_overlap = ConstraintList()

binary = {}
for i in model.TASKS:
    for j in model.TASKS:
        if i >= j:
            continue
        if task_dict[i][2] != task_dict[j][2]:
            continue
        binary[i, j] = Var(domain=Binary)
        model.add_component(f"binary_{i}_{j}", binary[i, j])
        model.no_overlap.add(expr=(
            model.end[i] <= model.start[j] + (1 - binary[i, j]) * 1e5
        ))
        model.no_overlap.add(expr=(
            model.start[i] >= model.end[j] + binary[i, j] * 1e5
        ))


# Calendar constraint: Ensure tasks run within machine working hours
model.calendar_constraint = ConstraintList()
for i in model.TASKS:
    machine = task_dict[i][2]
    working_minutes = calendar[machine]
    model.calendar_constraint.add(model.start[i] >= min(working_minutes))
    model.calendar_constraint.add(model.end[i] <= max(working_minutes) + 1)


# Makespan constraint
def makespan_rule(m, i):
    return m.makespan >= m.end[i]

model.make_span_con = Constraint(model.TASKS, rule=makespan_rule)

# Objective
model.obj = Objective(expr=model.makespan, sense=minimize)

# Scheduler
solver = SolverFactory('glpk')
result = solver.solve(model, tee=False)

print("Schedule:")
model.display()
print(task_dict)
# print(model.TASKS)
for i in model.TASKS:
    t = task_dict[i]
    print(f"{t[0]} - {t[1]} ({t[2]}): Start={model.start[i]():.1f} End={model.end[i]():.1f}")

print(f"\nTotal Makespan: {model.makespan():.1f} minutes")

# Visualization
schedule = []
for i in model.TASKS:
    job, task, machine, duration, _ = task_dict[i]
    start = model.start[i]()
    end = model.end[i]()
    schedule.append((job, task, machine, start, end))

# ------------------------------
# Gantt Chart Visualization
# ------------------------------
machine_lanes = {
    "LaserCutter": 0,
    "CNC_Mill": 1,
    "PaintStation": 2
}

colors = {
    "Job1": "skyblue",
    "Job2": "lightgreen",
    "Job3": "salmon"
}

fig, ax = plt.subplots(figsize=(10, 4))

for job, task, machine, start, end in schedule:
    ax.barh(machine_lanes[machine], end - start, left=start, height=0.4,
            color=colors.get(job, 'gray'), edgecolor='black')
    ax.text((start + end) / 2, machine_lanes[machine], f"{job}-{task}",
            ha='center', va='center', fontsize=8)

ax.set_yticks([0, 1, 2])
ax.set_yticklabels(["LaserCutter", "CNC_Mill", "PaintStation"])
ax.set_xlabel("Time (minutes)")
ax.set_title("Factory Schedule Gantt Chart")
ax.grid(True)

plt.tight_layout()
plt.show()

# metrics
from collections import defaultdict

# 1. Initialize tracking
machine_busy_time = defaultdict(float)
machine_available_time = {}

# 2. Calculate busy time per machine from the schedule
for job, task, machine, start, end in schedule:
    machine_busy_time[machine] += (end - start)

# 3. Calculate available time based on calendar
for machine, hours in calendar.items():
    # Count how many minutes the machine works per day
    available_minutes = len(hours)
    machine_available_time[machine] = available_minutes

# 4. Print utilization
print("\nMachine Utilization:")
for machine in machines:
    busy = machine_busy_time[machine]
    available = machine_available_time[machine]
    utilization = (busy / available) * 100 if available else 0
    print(f"{machine}: {utilization:.2f}% (Busy: {busy} min / Available: {available} min)")
