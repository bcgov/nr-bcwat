import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
from io import BytesIO


def create_landcover_visualization(json_file_or_dict):
    """
    Create complete landcover visualization with pie chart and data table

    Args:
        json_file_or_dict: Either path to JSON file or dict with data

    Returns:
        BytesIO containing the PNG image

    Expected data structure:
    {
        "overview": {
            "area_km2": 20907.08,
            "barren": 17.7,
            "coniferous": 50.0,
            ... etc
        }
    }
    """
    # Load data
    if isinstance(json_file_or_dict, str):
        with open(json_file_or_dict, 'r') as f:
            data = json.load(f)
    else:
        data = json_file_or_dict

    overview = data.get('overview', {})
    total_area = overview.get('area_km2', 0)

    # Your exact categories and colors
    categories = [
        {"name": "Barren", "key": "barren", "color": "#540000"},
        {"name": "Coniferous", "key": "coniferous", "color": "#005400"},
        {"name": "Cropland", "key": "cropland", "color": "#eca231"},
        {"name": "Deciduous", "key": "deciduous", "color": "#54aa00"},
        {"name": "Developed", "key": "developed", "color": "#f00"},
        {"name": "Grassland", "key": "grassland", "color": "#ffff7e"},
        {"name": "Herb", "key": "herb", "color": "#0a0"},
        {"name": "Mixed", "key": "mixed", "color": "#545400"},
        {"name": "Shrub", "key": "shrub", "color": "#af0"},
        {"name": "Snow / Glacier", "key": "snow", "color": "#cfcfcf"},
        {"name": "Water", "key": "water", "color": "#388edb"},
        {"name": "Wetland", "key": "wetland", "color": "#aa0"},
    ]

    # Extract data for pie chart and table
    pie_labels = []
    pie_sizes = []
    pie_colors = []
    table_data = []

    for cat in categories:
        percentage = overview.get(cat['key'], 0)
        if percentage is not None:
            area_km2 = total_area * percentage / 100.0

            # Add to table regardless of value
            table_data.append({
                'type': cat['name'],
                'color': cat['color'],
                'area': area_km2,
                'percentage': percentage
            })

            # Only add to pie if > 0
            if percentage > 0:
                pie_labels.append(cat['name'])
                pie_sizes.append(percentage)
                pie_colors.append(cat['color'])

    # Create figure with two subplots side by side
    fig = plt.figure(figsize=(14, 6))

    # Left side: Pie chart
    ax_pie = plt.subplot(1, 2, 1)

    wedges, texts = ax_pie.pie(
        pie_sizes,
        labels=None,  # Remove labels
        colors=pie_colors,
        autopct=None,  # Remove percentage labels
        startangle=90,
        textprops={'fontsize': 9, 'color': 'black'}
    )

    ax_pie.axis('equal')

    # Right side: Table
    ax_table = plt.subplot(1, 2, 2)
    ax_table.axis('off')

    # Prepare table data with empty first column for colors
    table_rows = []

    # Header row
    table_rows.append(['', 'Type', 'Area (km²)', '% of Watershed'])

    # Data rows
    for row in table_data:
        table_rows.append([
            '',  # Empty for color square
            row['type'],
            f"{row['area']:.1f}",
            f"{row['percentage']:.1f}%"
        ])

    # Create table
    table = ax_table.table(
        cellText=table_rows,
        cellLoc='left',
        loc='center',
        colWidths=[0.08, 0.35, 0.28, 0.29],  # Narrow first column for colors
        bbox=[0, 0, 1, 1]
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)

    # Remove all borders
    for key, cell in table.get_celld().items():
        cell.set_linewidth(0)
        cell.set_edgecolor('white')

    # Style header row
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#f0f0f0')
        if i > 0:  # Don't bold the empty color column header
            cell.set_text_props(weight='bold')

    # Add color squares
    for idx, row in enumerate(table_data, start=1):
        # Get the cell position
        cell = table[(idx, 0)]

        # Calculate position for color square (centered in the narrow column)
        y_pos = 1 - (idx + 0.5) / (len(table_data) + 1)

        # Draw small colored square
        color_patch = mpatches.Rectangle(
            (0.03, y_pos - 0.015),  # x, y position
            0.02,  # width (small square)
            0.03,  # height
            transform=ax_table.transAxes,
            facecolor=row['color'],
            edgecolor='black',
            linewidth=0.8
        )
        ax_table.add_patch(color_patch)

    # Align columns
    for (i, j), cell in table.get_celld().items():
        if j == 0:  # Color column
            cell.set_text_props(ha='center')
        elif j == 1:  # Type column
            cell.set_text_props(ha='left')
        else:  # Number columns
            cell.set_text_props(ha='right')

    plt.tight_layout()

    # Save to bytes
    buf = BytesIO()
    plt.savefig(
        buf,
        format='png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )
    buf.seek(0)
    plt.close(fig)

    return buf

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch

def create_pdf(output_path, image_path, watershed_name):
    doc = SimpleDocTemplate(output_path, pagesize=letter)

    # Base styles
    styles = getSampleStyleSheet()

    # Custom H1 style
    styles.add(ParagraphStyle(
        name="H1",
        parent=styles["Heading1"],
        fontSize=24,
        leading=28,
        spaceAfter=12,
        spaceBefore=12,
        alignment=TA_LEFT,
    ))

    # Custom body paragraph style
    styles.add(ParagraphStyle(
        name="BodyTextLarge",
        parent=styles["BodyText"],
        fontSize=12,
        leading=16,
        spaceAfter=14,
    ))

    story = []

    # --- Render Header ---
    story.append(Paragraph("Landcover", styles["H1"]))
    story.append(Spacer(1, 0.2 * inch))

    # --- Render Body Text ---
    text = f"""
    The landcover characteristics influence hydrologic processes in a watershed.
    The chart below shows the landcover makeup of the <b>{watershed_name}</b> watershed.
    These components were incorporated into the hydrologic model that produces
    the water supply estimates in this report, primarily influencing the
    evapotranspiration component of the water budget calculations, which represent
    the amount of water that moves directly back to the atmosphere through direct
    evaporation or transpiration by vegetation.
    """

    story.append(Paragraph(text, styles["BodyTextLarge"]))
    story.append(Spacer(1, 0.3 * inch))

    # --- Add Image ---
    img = Image(image_path)
    img.drawWidth = 500
    img.drawHeight = 266
    story.append(img)

    # Build final PDF
    doc.build(story)

# Test it
if __name__ == '__main__':
    import time

    start_time = time.time()

    end_time = time.time()
    elapsed_time = end_time - start_time
    # Load from fixture
    chart = create_landcover_visualization('fixtures/overview.json')

    # Save to file
    with open('landcover.png', 'wb') as f:
        f.write(chart.getvalue())

    print("✓ Complete visualization created: landcover_complete.png")
    print("✓ Includes: Pie chart + Data table")
    print("✓ Data loaded from: fixtures/overview.json")

    create_pdf(
        "landcover.pdf",
        'landcover.png',
        watershed_name='Kinbasket'
    )

    print("✓ Created PDF Using Image")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"--- {elapsed_time:.4f} seconds ---")
