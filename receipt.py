# receipt.py
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def generate_receipt_image(order_id, user_name, product_name, price, size, phone):
    # 1. Create clean canvas (600x800)
    width, height = 600, 800
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    # 2. Modern Borders
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#2C3E50", width=3)
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline="#BDC3C7", width=1)
    
    # 3. Load Default Font with controlled sizes (No external file needed!)
    title_font = ImageFont.load_default(size=30)
    body_font = ImageFont.load_default(size=20)
    bold_font = ImageFont.load_default(size=22)

    # 4. Header
    draw.text((width/2, 60), "ETHIO SHOE STORE", fill="#2C3E50", font=title_font, anchor="mm")
    draw.text((width/2, 100), "Official Sales Receipt", fill="#7F8C8D", font=body_font, anchor="mm")
    
    # Divider Line
    draw.line([(40, 130), (width - 40, 130)], fill="#BDC3C7", width=2)
    
    # 5. Order Information
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    info_data = [
        ("Order ID:", f"#ETH-{order_id}", True),
        ("Date:", current_date, False),
        ("Customer:", user_name, False),
        ("Phone:", phone, False),
    ]
    
    y_offset = 160
    for label, value, is_bold in info_data:
        fnt = bold_font if is_bold else body_font
        clr = "#2C3E50" if is_bold else "#34495E"
        draw.text((50, y_offset), label, fill="#7F8C8D", font=body_font)
        draw.text((280, y_offset), value, fill=clr, font=fnt)
        y_offset += 40
        
    # Divider Line
    draw.line([(40, y_offset + 10), (width - 40, y_offset + 10)], fill="#BDC3C7", width=2)
    
    # 6. Product Details
    y_offset += 40
    draw.text((50, y_offset), "Order Items", fill="#2C3E50", font=bold_font)
    
    y_offset += 45
    draw.text((50, y_offset), f"Item: {product_name}", fill="#34495E", font=body_font)
    draw.text((450, y_offset), f"Size: {size}", fill="#34495E", font=body_font)
    
    # Total Amount Box
    y_offset += 70
    draw.rectangle([(40, y_offset), (width - 40, y_offset + 60)], fill="#F8F9F9", outline="#BDC3C7")
    draw.text((60, y_offset + 18), "Total Amount:", fill="#2C3E50", font=bold_font)
    draw.text((420, y_offset + 18), f"{price} ETB", fill="#E74C3C", font=bold_font)
    
    # 7. Footer Notes
    y_offset += 130
    draw.text((width/2, y_offset), "⚠️ Please forward this receipt to the admin to confirm payment.", fill="#7F8C8D", font=body_font, anchor="mm")
    draw.text((width/2, y_offset + 40), "Thank you for shopping with us!", fill="#2C3E50", font=bold_font, anchor="mm")
    
    # 8. Save Image
    filename = f"receipt_{order_id}.png"
    image.save(filename)
    return filename