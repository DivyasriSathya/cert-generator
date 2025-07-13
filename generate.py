from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from math import radians, sin, cos
import os
from datetime import date
from datetime import datetime
from google_gemini import generate_message  # You must define this or mock it
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import simpleSplit
# Register fonts (adjust path if needed)
pdfmetrics.registerFont(TTFont('Roboto-Bold', 'assets/fonts/Roboto-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-Regular', 'assets/fonts/Roboto-Regular.ttf'))

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_curved_text(c, text, center_x, center_y, radius, start_angle_deg=180, char_angle_deg=12, font_name="Times-Bold", font_size=14):
    c.setFont(font_name, font_size)
    c.setFillColor(HexColor("#000000"))

    angle = start_angle_deg
    for char in text:
        rad = radians(angle)
        x = center_x + radius * cos(rad)
        y = center_y + radius * sin(rad)
        c.saveState()
        c.translate(x, y)
        c.rotate(angle - 90)
        c.drawString(0, 0, char)
        c.restoreState()
        angle += char_angle_deg

def draw_certificate(name, cert_type, event_title, event_date):
    try:
        event_date_obj = datetime.strptime(event_date, "%Y-%m-%d")
        formatted_date = event_date_obj.strftime("%d %B %Y")
    except ValueError:
        formatted_date = event_date
    output_path = os.path.join(OUTPUT_DIR, f"{name.replace(' ', '_')}_{cert_type}.pdf")
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    # === Borders ===
    BORDER_THICKNESS = 5
    MARGIN = 15  # gap from edge

    # Blue Top Border
    c.setFillColor(HexColor("#0072CE"))
    c.rect(MARGIN, height - MARGIN - BORDER_THICKNESS, width - 2*MARGIN, BORDER_THICKNESS, fill=1, stroke=0)

    # Green Left Border
    c.setFillColor(HexColor("#00A859"))
    c.rect(MARGIN, MARGIN, BORDER_THICKNESS, height - 2*MARGIN, fill=1, stroke=0)

    # Red Right Border
    c.setFillColor(HexColor("#D62828"))
    c.rect(width - MARGIN - BORDER_THICKNESS, MARGIN, BORDER_THICKNESS, height - 2*MARGIN, fill=1, stroke=0)

    # Yellow Bottom Border
    c.setFillColor(HexColor("#FFD700"))
    c.rect(MARGIN, MARGIN, width - 2*MARGIN, BORDER_THICKNESS, fill=1, stroke=0)


    # === Logos ===
    logo_height = 70  # Increased size
    logo_width = 70
    banner_width = 220
    banner_height = 60
    logo_y = height - 100  # Vertically aligned slightly lower

    # Adjust center to visually ignore left blue badge (120px wide)
    center_x = (width + 150) / 2

    try:
        c.drawImage("assets/logo_gsss.png",
                    center_x - (banner_width / 2) - logo_width - 5,
                    logo_y,
                    width=logo_width - 5,
                    height=logo_height,
                    mask='auto')

        c.drawImage("assets/gsssietw_name.png",
                    center_x - (banner_width / 2),
                    logo_y + 5,
                    width=banner_width,
                    height=banner_height,
                    mask='auto')

        c.drawImage("assets/logo_aiml.png",
                    center_x + (banner_width / 2) + 5,
                    logo_y - 5,
                    width=logo_width + 15,
                    height=logo_height + 10,
                    mask='auto')
    except Exception as e:
        print(f"⚠️ Logo error: {e}")

    # === Left Blue Pentagon Badge with GCC Logo ===
    try:
        from reportlab.pdfgen import pathobject

        # Updated dimensions
        badge_top = height - 20       # Align with top blue border (leave margin)
        badge_bottom = height / 2 - 150  # Same bottom as before
        badge_left = 40
        badge_width = 150
        badge_center_x = badge_left + badge_width / 2
        point_height = 50  # Downward triangle depth

        # Draw taller pentagon badge starting from top
        c.setFillColor(HexColor("#0072CE"))
        path = c.beginPath()
        path.moveTo(badge_left, badge_top)  # Top-left
        path.lineTo(badge_left + badge_width, badge_top)  # Top-right
        path.lineTo(badge_left + badge_width, badge_bottom + point_height)  # Bottom-right
        path.lineTo(badge_center_x, badge_bottom - point_height)  # Bottom tip
        path.lineTo(badge_left, badge_bottom + point_height)  # Bottom-left
        path.close()
        c.drawPath(path, fill=1, stroke=0)

        # Updated logo placement - move slightly up
        gcc_logo_size = 200
        logo_x = badge_center_x - gcc_logo_size / 2
        logo_y = (badge_top + badge_bottom) / 2 - gcc_logo_size / 2 + 10  # Center logo vertically in badge
        c.drawImage("assets/logo_gcc.png", logo_x, logo_y, width=gcc_logo_size, height=gcc_logo_size, mask='auto')

    except Exception as e:
        print(f"⚠️ Pentagon badge error: {e}")

    # === Fonts: Use Times New Roman ===
    c.setFont("Times-Bold", 30)
    c.setFillColor(HexColor("#000000"))

    # === Adjusted Center (ignoring blue badge space) ===
    adjusted_center = (width + 150) / 2  # Shift right to ignore blue badge (adjust 100 as needed)

    # === Event Title ===
    c.drawCentredString(adjusted_center, height - 150, event_title.upper())

    # === Organized By (split into 2 lines) ===
    c.setFont("Times-Roman", 16)
    c.drawCentredString(adjusted_center, height - 178, "Organized by")
    c.drawCentredString(adjusted_center, height - 196, "Google Cloud Students Club, Department of CSE(AI&ML)")

    # === Draw Certificate Type Ribbon Image (Based on cert_type from dropdown) ===
    try:
        ribbon_center_x = (width + 150) / 2
        ribbon_center_y = height - 270  # Adjust this to shift the ribbon up/down
        ribbon_width = 320
        ribbon_height = 90

        # Normalize cert_type to title case (e.g., "winner" → "Winner")
        cert_type_key = cert_type.strip().split()[0].capitalize()

        # Map cert_type to image paths
        ribbon_images = {
            "Participation": "assets/participation_ribbon.png",
            "Appreciation": "assets/appreciation_ribbon.png",
            "Winner": "assets/winner_ribbon.png",
            "Runner": "assets/runner_ribbon.png"
        }

        # Get corresponding image path, default to participation if not found
        ribbon_path = ribbon_images.get(cert_type_key, ribbon_images["Participation"])

        c.drawImage(
            ribbon_path,
            ribbon_center_x - ribbon_width / 2,
            ribbon_center_y - ribbon_height / 2,
            width=ribbon_width,
            height=ribbon_height,
            mask='auto'
        )

    except Exception as e:
        print(f"⚠️ Ribbon image error: {e}")

    # === Certificate Message (Single centered paragraph) ===
    try:
        message = generate_message(name, event_title, cert_type, formatted_date)
    except:
        message = (
            f"This is to certify that {name} from GSSSIETW has actively participated in {event_title} held on {formatted_date}. "
            f"Your contribution to {event_title} as a {cert_type} was sincerely appreciated. Well done, {name}!"
        )

    # Layout settings
    font_size = 16
    message_y = height - 340  # vertical start (adjust lower if needed)
    box_height = 100          # height of message area

    # Define margins to fit between badge and red border
    left_margin = 260
    right_margin = 80
    box_width = width - left_margin - right_margin

    # Paragraph style
    style = ParagraphStyle(
        name='Centered',
        fontName='Times-Roman',
        fontSize=font_size,
        alignment=TA_CENTER,
        leading=font_size + 4
    )

    # Create Paragraph
    paragraph = Paragraph(message, style)

    # Create a Frame to render the paragraph
    frame = Frame(
        x1=left_margin,
        y1=message_y - box_height,  # bottom y
        width=box_width,
        height=box_height,
        showBoundary=0  # set to 1 for debugging layout
    )

    # Render paragraph inside frame
    frame.addFromList([paragraph], c)

    # === Footer Signatures (with adjusted alignment and spacing) ===

    # Font settings
    name_font = "Times-Bold"
    title_font = "Times-Roman"
    name_size = 14
    title_size = 12

    # Left block (shifted to avoid blue badge)
    left_x = 230  # shifted right to leave space for blue badge
    left_y = 100
    line_gap = 15

    c.setFont(name_font, name_size)
    c.drawCentredString(left_x, left_y, "Dr. Manjuprasad B")

    c.setFont(title_font, title_size)
    c.drawCentredString(left_x, left_y - line_gap, "Prof & HOD. Dept of CSE(AI&ML)")
    c.drawCentredString(left_x, left_y - (line_gap * 2), "GSSSIETW, Mysuru")

    # Right block
    right_x = width - 140  # same margin from right side
    right_y = 100

    c.setFont(name_font, name_size)
    c.drawCentredString(right_x, right_y, "Dr. Shivakumar M")

    c.setFont(title_font, title_size)
    c.drawCentredString(right_x, right_y - line_gap, "Principal")
    c.drawCentredString(right_x, right_y - (line_gap * 2), "GSSSIETW, Mysuru")

    c.save()
    print(f"✅ Certificate saved to: {output_path}")
    return output_path
