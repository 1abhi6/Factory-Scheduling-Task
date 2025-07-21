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

# Constraint
# Duaration constraint
def duration_rule(m, i):
    return m.end[i] == m.start[i] + task_dict[i][3]

model.task_duration = Constraint(model.TASKS, rule=duration_rule)

# Precedence constraint
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

# Calendar constraint
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
# model.display()
# print(task_dict)
# print(model.TASKS)
for i in model.TASKS:
    t = task_dict[i]
    print(f"{t[0]} - {t[1]} ({t[2]}): Start={model.start[i]():.1f} End={model.end[i]():.1f}")

print(f"\nTotal Makespan: {model.makespan():.1f} minutes")