def get_calendar():
    return {
        'LaserCutter': list(range(480, 1020)),
        'CNC_Mill': list(range(480, 960)),
        'PaintStation': list(range(540, 1080)),
    }

def get_tasks():
    return [
        ('Job1', 'Cutting', 'LaserCutter', 180, None),
        ('Job1', 'Milling', 'CNC_Mill', 120, 'Cutting'),
        ('Job1', 'Painting', 'PaintStation', 60, 'Milling'),
        ('Job2', 'Cutting', 'LaserCutter', 120, None),
        ('Job2', 'Painting', 'PaintStation', 60, 'Cutting'),
        ('Job3', 'Milling', 'CNC_Mill', 240, None),
        ('Job3', 'Painting', 'PaintStation', 120, 'Milling'),
    ]
