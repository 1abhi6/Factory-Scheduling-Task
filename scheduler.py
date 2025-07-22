from pyomo.environ import SolverFactory

def solve_model(model):
    solver = SolverFactory('glpk')
    solver.solve(model)

def extract_schedule(model, task_dict):
    schedule = []
    for i in model.TASKS:
        job, task, machine, *_ = task_dict[i]
        start = model.start[i]()
        end = model.end[i]()
        schedule.append((job, task, machine, start, end))
    return schedule
