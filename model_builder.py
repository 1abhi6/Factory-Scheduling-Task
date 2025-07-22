from pyomo.environ import *

def build_model(tasks, calendar):
    model = ConcreteModel()
    model.TASKS = RangeSet(0, len(tasks)-1)
    task_dict = {i: t for i, t in enumerate(tasks)}

    model.start = Var(model.TASKS, domain=NonNegativeReals)
    model.end = Var(model.TASKS, domain=NonNegativeReals)
    model.makespan = Var(domain=NonNegativeReals)

    # Task Duration
    def duration_rule(m, i):
        return m.end[i] == m.start[i] + task_dict[i][3]
    model.task_duration = Constraint(model.TASKS, rule=duration_rule)

    # Precedence
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

    # No Overlap on Same Machine
    model.no_overlap = ConstraintList()
    binary = {}
    for i in model.TASKS:
        for j in model.TASKS:
            if i >= j or task_dict[i][2] != task_dict[j][2]:
                continue
            binary[i, j] = Var(domain=Binary)
            model.add_component(f"binary_{i}_{j}", binary[i, j])
            model.no_overlap.add(model.end[i] <= model.start[j] + (1 - binary[i, j]) * 1e5)
            model.no_overlap.add(model.start[i] >= model.end[j] + binary[i, j] * 1e5)

    # Makespan Constraint
    def makespan_rule(m, i):
        return m.makespan >= m.end[i]
    model.make_span_con = Constraint(model.TASKS, rule=makespan_rule)

    # Calendar Constraint
    model.calendar_constraint = ConstraintList()
    for i in model.TASKS:
        machine = task_dict[i][2]
        working_minutes = calendar[machine]
        model.calendar_constraint.add(model.start[i] >= min(working_minutes))
        model.calendar_constraint.add(model.end[i] <= max(working_minutes) + 1)

    # Objective
    model.obj = Objective(expr=model.makespan, sense=minimize)

    return model, task_dict
