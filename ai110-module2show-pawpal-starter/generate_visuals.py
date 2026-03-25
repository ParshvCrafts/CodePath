"""
Generate PawPal+ mockup screenshot and convert UML to PNG
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

# Create a mockup screenshot of the Streamlit app
def create_mockup_screenshot():
    """Create a professional mockup of the PawPal+ Streamlit UI"""

    # Image dimensions
    width, height = 1400, 900

    # Create image with white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Define colors
    PRIMARY_COLOR = '#0068C9'  # Streamlit blue
    SECONDARY_COLOR = '#83C9F9'
    TEXT_COLOR = '#31333F'
    BORDER_COLOR = '#E0E0E0'
    BG_LIGHT = '#F5F5F5'
    SUCCESS_COLOR = '#09AB3B'
    WARNING_COLOR = '#FFA421'

    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        header_font = ImageFont.truetype("arial.ttf", 20)
        body_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        # Fallback if fonts not available
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw header bar
    draw.rectangle([(0, 0), (width, 80)], fill=PRIMARY_COLOR)

    # Draw title
    title_text = "PawPal+ - Pet Care Scheduler"
    draw.text((30, 20), title_text, fill='white', font=title_font)

    # Draw main content
    y_pos = 100

    # Owner Profile Section
    draw.rectangle([(20, y_pos), (width-20, y_pos+60)], outline=BORDER_COLOR, width=2)
    draw.text((40, y_pos+10), "Owner Profile", fill=TEXT_COLOR, font=header_font)
    draw.text((40, y_pos+35), "Owner: Jordan  |  Available Hours: 6.0  |  Pets: 2", fill=TEXT_COLOR, font=body_font)

    y_pos += 80

    # Pet Management Section
    draw.text((20, y_pos), "Pet Management", fill=TEXT_COLOR, font=header_font)
    y_pos += 35

    # Pet boxes
    draw.rectangle([(20, y_pos), (680, y_pos+80)], fill=BG_LIGHT, outline=BORDER_COLOR, width=2)
    draw.text((40, y_pos+10), "Mochi (Dog, Golden Retriever, age 3)", fill=TEXT_COLOR, font=body_font)
    draw.text((40, y_pos+35), "Tasks: 3 | Priority: [HIGH, MEDIUM]", fill=TEXT_COLOR, font=small_font)
    draw.text((40, y_pos+55), "Status: [X] Complete [X] Recurring [X] Daily", fill=SUCCESS_COLOR, font=small_font)

    draw.rectangle([(720, y_pos), (1380, y_pos+80)], fill=BG_LIGHT, outline=BORDER_COLOR, width=2)
    draw.text((740, y_pos+10), "Luna (Cat, Siamese, age 5)", fill=TEXT_COLOR, font=body_font)
    draw.text((740, y_pos+35), "Tasks: 2 | Priority: [HIGH, MEDIUM]", fill=TEXT_COLOR, font=small_font)
    draw.text((740, y_pos+55), "Status: [X] Complete [X] Recurring [X] Daily", fill=SUCCESS_COLOR, font=small_font)

    y_pos += 100

    # Task Management Section
    draw.text((20, y_pos), "Task Management - Mochi", fill=TEXT_COLOR, font=header_font)
    y_pos += 35

    # Filter controls
    draw.rectangle([(20, y_pos), (1380, y_pos+35)], fill=BG_LIGHT, outline=BORDER_COLOR, width=1)
    draw.text((40, y_pos+8), "Filter: [All] [Complete] [Incomplete]  |  Sort: [Added] [Time] [Priority]  |  Priority: [All] [HIGH] [MEDIUM]",
              fill=TEXT_COLOR, font=small_font)

    y_pos += 45

    # Tasks table
    tasks_data = [
        ("Morning walk (Mochi)", "30 min", "HIGH", "Daily", "[ ]"),
        ("Morning feeding (Mochi)", "15 min", "HIGH", "Daily", "[ ]"),
        ("Play time (Mochi)", "20 min", "MEDIUM", "Daily", "[ ]"),
    ]

    # Table header
    draw.rectangle([(20, y_pos), (1380, y_pos+25)], fill=SECONDARY_COLOR)
    col_x = [40, 300, 500, 650, 800]
    headers = ["Description", "Duration", "Priority", "Frequency", "Status"]
    for i, header in enumerate(headers):
        draw.text((col_x[i], y_pos+5), header, fill='white', font=small_font)

    y_pos += 25

    # Table rows
    for task in tasks_data:
        draw.rectangle([(20, y_pos), (1380, y_pos+22)], outline=BORDER_COLOR, width=1)
        for i, cell in enumerate(task):
            draw.text((col_x[i], y_pos+4), cell, fill=TEXT_COLOR, font=small_font)
        y_pos += 22

    # Save screenshot
    screenshot_path = Path(__file__).parent / "pawpal_demo.png"
    img.save(str(screenshot_path))
    print(f"[SUCCESS] Mockup screenshot saved to {screenshot_path}")
    return screenshot_path


def convert_uml_to_png():
    """Convert Mermaid UML diagram to PNG using text rendering"""

    # For now, create a text-based UML diagram as PNG
    # This demonstrates the class structure

    img = Image.new('RGB', (1200, 1400), color='white')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 18)
        body_font = ImageFont.truetype("arial.ttf", 12)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Title
    draw.text((20, 20), "PawPal+ System Architecture (UML Class Diagram)", fill='#0068C9', font=title_font)

    y = 60
    box_width = 280
    box_height = 280

    # Owner class
    draw.rectangle([(20, y), (20+box_width, y+box_height)], outline='#000000', width=2)
    draw.line([(20, y+30), (20+box_width, y+30)], fill='#000000', width=2)
    draw.line([(20, y+150), (20+box_width, y+150)], fill='#000000', width=2)
    draw.text((30, y+10), "Owner", fill='#000000', font=body_font)

    owner_attrs = [
        "-name: str",
        "-available_hours: float",
        "-pets: List[Pet]",
    ]
    for i, attr in enumerate(owner_attrs):
        draw.text((30, y+40+i*20), attr, fill='#333333', font=small_font)

    owner_methods = [
        "+add_pet()",
        "+get_pets()",
        "+get_all_tasks()",
        "+filter_tasks_by_status()",
    ]
    for i, method in enumerate(owner_methods):
        draw.text((30, y+160+i*20), method, fill='#333333', font=small_font)

    # Pet class
    x_pet = 320
    draw.rectangle([(x_pet, y), (x_pet+box_width, y+box_height)], outline='#000000', width=2)
    draw.line([(x_pet, y+30), (x_pet+box_width, y+30)], fill='#000000', width=2)
    draw.line([(x_pet, y+150), (x_pet+box_width, y+150)], fill='#000000', width=2)
    draw.text((x_pet+30, y+10), "Pet", fill='#000000', font=body_font)

    pet_attrs = [
        "-name: str",
        "-species: str",
        "-age: int",
        "-tasks: List[Task]",
    ]
    for i, attr in enumerate(pet_attrs):
        draw.text((x_pet+30, y+40+i*20), attr, fill='#333333', font=small_font)

    pet_methods = [
        "+add_task()",
        "+get_tasks()",
        "+filter_tasks_by_status()",
        "+get_tasks_sorted_by_time()",
    ]
    for i, method in enumerate(pet_methods):
        draw.text((x_pet+30, y+160+i*20), method, fill='#333333', font=small_font)

    # Task class
    x_task = 620
    draw.rectangle([(x_task, y), (x_task+box_width, y+box_height)], outline='#000000', width=2)
    draw.line([(x_task, y+30), (x_task+box_width, y+30)], fill='#000000', width=2)
    draw.line([(x_task, y+170), (x_task+box_width, y+170)], fill='#000000', width=2)
    draw.text((x_task+30, y+10), "Task", fill='#000000', font=body_font)

    task_attrs = [
        "-task_id: str",
        "-description: str",
        "-duration_minutes: int",
        "-priority: Priority",
        "-frequency: Frequency",
    ]
    for i, attr in enumerate(task_attrs):
        draw.text((x_task+30, y+40+i*20), attr, fill='#333333', font=small_font)

    task_methods = [
        "+mark_complete()",
        "+is_urgent()",
        "+create_next_occurrence()",
    ]
    for i, method in enumerate(task_methods):
        draw.text((x_task+30, y+180+i*20), method, fill='#333333', font=small_font)

    # Relationships
    draw.line([(300, y+150), (320, y+150)], fill='#0068C9', width=2)
    draw.text((310, y+120), "1:many", fill='#0068C9', font=small_font)

    draw.line([(600, y+150), (620, y+150)], fill='#0068C9', width=2)
    draw.text((610, y+120), "1:many", fill='#0068C9', font=small_font)

    # Scheduler class
    y2 = y + 350
    draw.rectangle([(20, y2), (20+box_width, y2+box_height)], outline='#000000', width=2)
    draw.line([(20, y2+30), (20+box_width, y2+30)], fill='#000000', width=2)
    draw.line([(20, y2+100), (20+box_width, y2+100)], fill='#000000', width=2)
    draw.text((30, y2+10), "Scheduler", fill='#000000', font=body_font)

    scheduler_methods = [
        "+create_daily_schedule()",
        "+detect_conflicts()",
        "-prioritize_tasks()",
        "-fit_tasks_in_day()",
    ]
    for i, method in enumerate(scheduler_methods):
        draw.text((30, y2+40+i*20), method, fill='#333333', font=small_font)

    # Schedule class
    draw.rectangle([(320, y2), (320+box_width, y2+box_height)], outline='#000000', width=2)
    draw.line([(320, y2+30), (320+box_width, y2+30)], fill='#000000', width=2)
    draw.line([(320, y2+100), (320+box_width, y2+100)], fill='#000000', width=2)
    draw.text((350, y2+10), "Schedule", fill='#000000', font=body_font)

    schedule_attrs = [
        "-scheduled_tasks: List",
        "-schedule_date: date",
    ]
    for i, attr in enumerate(schedule_attrs):
        draw.text((350, y2+40+i*20), attr, fill='#333333', font=small_font)

    schedule_methods = [
        "+add_scheduled_task()",
        "+get_tasks_by_time()",
        "+get_explanation()",
    ]
    for i, method in enumerate(schedule_methods):
        draw.text((350, y2+110+i*20), method, fill='#333333', font=small_font)

    # Connection
    draw.line([(300, y2+150), (320, y2+150)], fill='#0068C9', width=2)

    # Add legend
    legend_y = y2 + 350
    draw.text((20, legend_y), "Class Diagram Legend:", fill='#0068C9', font=body_font)
    draw.text((20, legend_y+30), "- = Private attribute  |  + = Public method  |  1:many = One-to-many relationship",
              fill='#333333', font=small_font)

    # Save diagram
    uml_path = Path(__file__).parent / "uml_final.png"
    img.save(str(uml_path))
    print(f"[SUCCESS] UML diagram saved to {uml_path}")
    return uml_path


if __name__ == "__main__":
    print("Generating PawPal+ visuals...")
    create_mockup_screenshot()
    convert_uml_to_png()
    print("\n[SUCCESS] All visuals generated successfully!")
