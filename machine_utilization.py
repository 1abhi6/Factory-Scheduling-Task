from collections import defaultdict

def calculate_utilization(schedule, calendar):
    machine_busy = defaultdict(float)
    utilization = {}

    for job, task, machine, start, end in schedule:
        machine_busy[machine] += end - start

    for machine, hours in calendar.items():
        available = len(hours)
        busy = machine_busy[machine]
        utilization[machine] = (busy / available) * 100 if available else 0

    return utilization
