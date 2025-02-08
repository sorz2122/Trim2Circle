from flask import Flask, request, render_template, send_file
import os
from PIL import Image, ImageDraw, ImageOps
import io
import zipfile
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, A3, A5, B4, B5, TABLOID
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
import logging

# Ensure pdf2image is installed
try:
    from pdf2image import convert_from_bytes
except ImportError:
    raise ImportError("pdf2image module is not installed. Please install it using 'pip install pdf2image'.")

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    diameter_mm = int(request.form['diameter']) if 'diameter' in request.form else None
    margin_mm = int(request.form['margin']) if 'margin' in request.form else 10
    spacing_mm = int(request.form['spacing']) if 'spacing' in request.form else 5
    add_border = 'add_border' in request.form
    border_width_mm = float(request.form['border_width']) if add_border else 0.0
    output_format = request.form['output_format'].lower()
    paper_size = request.form['paper_size']
    input_files = request.files.getlist('input_files')

    images = []
    for file in input_files:
        if file.filename.endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file.stream).convert("RGBA")
            if diameter_mm:
                image = resize_image(image, diameter_mm)
                output_image = crop_to_circle(image, diameter_mm, add_border, border_width_mm)
            else:
                output_image = image
            images.append(output_image)

    if output_format == 'pdf':
        pdf_buffer = io.BytesIO()
        create_pdf(images, diameter_mm, margin_mm, spacing_mm, pdf_buffer, paper_size)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='processed_images.pdf')
    elif output_format == 'png':
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for i, image in enumerate(images):
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                zf.writestr(f'image_{i+1}.png', img_buffer.read())
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='processed_images.zip')
    else:
        return "Invalid output format", 400

def mm_to_pixels(mm, dpi):
    return int(mm * 0.0393701 * dpi)

def mm_to_points(mm):
    return mm * 2.83465

canon_selphy = (10*cm, 14.8*cm)

def get_paper_size(size_name):
    sizes = {
        'A3': A3,
        'A4': A4,
        'A5': A5,
        'LETTER': LETTER,
        'LEGAL': LEGAL,
        'B4': B4,
        'B5': B5,
        'TABLOID': TABLOID,
        'CANON_SELPHY': canon_selphy
    }
    return sizes.get(size_name, A4)

def create_pdf(images, diameter_mm, margin_mm, spacing_mm, buffer, paper_size):
    page_size = get_paper_size(paper_size)
    c = canvas.Canvas(buffer, pagesize=page_size)
    diameter_points = mm_to_points(diameter_mm) if diameter_mm else None
    margin_points = mm_to_points(margin_mm)
    spacing_points = mm_to_points(spacing_mm)
    page_width, page_height = page_size

    x = margin_points
    y = page_height - margin_points - (diameter_points if diameter_points else 0)

    for image in images:
        if diameter_points and x + diameter_points > page_width - margin_points:
            x = margin_points
            y -= diameter_points + spacing_points
            if y < margin_points:
                c.showPage()
                y = page_height - margin_points - diameter_points

        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        c.drawImage(ImageReader(img_buffer), x, y, width=diameter_points, height=diameter_points, mask='auto')
        x += diameter_points + spacing_points

    c.save()

def resize_image(image, diameter_mm):
    diameter_pixels = mm_to_pixels(diameter_mm, 300)
    return image.resize((diameter_pixels, diameter_pixels), Image.LANCZOS)

def crop_to_circle(image, diameter_mm, add_border=False, border_width_mm=0.1):
    diameter_pixels = mm_to_pixels(diameter_mm, 300)
    
    # Stelle sicher, dass das Bild quadratisch ist
    width, height = image.size
    if width != height:
        size = min(width, height)
        left = (width - size) / 2
        top = (height - size) / 2
        right = (width + size) / 2
        bottom = (height + size) / 2
        image = image.crop((left, top, right, bottom))
        image = image.resize((diameter_pixels, diameter_pixels), Image.LANCZOS)

    # Erstelle eine Maske für den Kreis
    mask = Image.new('L', (diameter_pixels, diameter_pixels), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter_pixels, diameter_pixels), fill=255)

    # Schneide das Bild auf die Kreisform zu
    result = Image.new('RGBA', (diameter_pixels, diameter_pixels), (0, 0, 0, 0))  # Transparenter Hintergrund
    result.paste(image, (0, 0), mask=mask)

    # Füge einen schwarzen Rand hinzu (falls aktiviert)
    if add_border:
        border_pixels = mm_to_pixels(border_width_mm, 300)
        border_layer = Image.new('RGBA', (diameter_pixels, diameter_pixels), (0, 0, 0, 0))  # Transparenter Hintergrund
        border_draw = ImageDraw.Draw(border_layer)
        border_draw.ellipse(
            (0, 0, diameter_pixels, diameter_pixels),
            outline=(0, 0, 0, 255),  # Schwarzer Rand
            width=border_pixels
        )
        result = Image.alpha_composite(result, border_layer)

    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
