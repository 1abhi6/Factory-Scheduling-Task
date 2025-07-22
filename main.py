from data_loader import get_calendar, get_tasks
from model_builder import build_model
from scheduler import solve_model, extract_schedule
from machine_utilization import calculate_utilization
from visualizer import plot_gantt

def main():
    # machines = ['LaserCutter', 'CNC_Mill', 'PaintStation']

    calendar = get_calendar()
    tasks = get_tasks()
    
    model, task_dict = build_model(tasks, calendar)
    solve_model(model)
    
    # Print details
    schedule = extract_schedule(model, task_dict)
    for entry in schedule:
        print(f"{entry[0]} - {entry[1]} ({entry[2]}): Start={entry[3]:.1f} End={entry[4]:.1f}")
    
    print(f"\nTotal Makespan: {model.makespan():.1f} minutes")
    
    # Calculate machine Utilization
    util = calculate_utilization(schedule, calendar)
    print("\nMachine Utilization:")
    # print(util)
    for m, u in util.items():
        print(f"{m}: {u:.2f}%")
        
    # Plot Gantt chart
    plot_gantt(schedule)

if __name__ == "__main__":
    main()
