from io import BytesIO

import barcode
from PIL import Image, ImageDraw, ImageFont


WIDTH = 390
HEIGHT = 128
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def generate_ptouch_label(code):
    """Generate a 24 mm Brother P-touch label as monochrome PNG bytes."""

    code = str(code)

    if len(code) != 13 or not code.isdigit():
        raise ValueError("Expected a 13-digit EAN-13 barcode")

    EAN = barcode.get_barcode_class("ean13")
    ean = EAN(code[:12])

    if ean.get_fullcode() != code:
        raise ValueError("Invalid EAN-13 check digit")

    img = Image.new("1", (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(img)

    # Rounded border
    draw.rounded_rectangle(
        (3, 3, WIDTH - 4, HEIGHT - 4),
        radius=19,
        outline=0,
        width=3,
    )

    # Fonts
    name_font = ImageFont.truetype(FONT_PATH, 20)
    number_font = ImageFont.truetype(FONT_PATH, 17)

    # Vertical Sherlock text
    text = "Sherlock"
    bbox = draw.textbbox((0, 0), text, font=name_font)

    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    text_img = Image.new("1", (tw + 4, th + 4), 1)
    td = ImageDraw.Draw(text_img)
    td.text(
        (2 - bbox[0], 2 - bbox[1]),
        text,
        font=name_font,
        fill=0,
    )

    text_img = text_img.rotate(90, expand=True)

    img.paste(
        text_img,
        (8, (HEIGHT - text_img.height) // 2),
    )

    # Draw genuine EAN-13 barcode
    pattern = ean.build()[0]

    module_width = 2
    bar_height = 65

    barcode_width = len(pattern) * module_width
    start_x = 57 + (WIDTH - 57 - barcode_width) // 2
    start_y = 17

    for i, bit in enumerate(pattern):
        if bit == "1":
            x = start_x + i * module_width
            draw.rectangle(
                (
                    x,
                    start_y,
                    x + module_width - 1,
                    start_y + bar_height - 1,
                ),
                fill=0,
            )

    # Print full barcode number
    bbox = draw.textbbox((0, 0), code, font=number_font)
    number_width = bbox[2] - bbox[0]

    draw.text(
        (
            57 + (WIDTH - 57 - number_width) // 2,
            89,
        ),
        code,
        font=number_font,
        fill=0,
    )

    output = BytesIO()
    img.save(output, format="PNG")

    return output.getvalue()
