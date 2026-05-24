# receipt.py
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def generate_receipt_image(order_id, user_name, product_name, price, size, phone):
    # 1. ንጹህ ነጭ ወረቀት ማዘጋጀት (ስፋት 650px፣ ቁመት 900px - ለጽሑፍ ምቾት ሰፋ ተደርጓል)
    width, height = 650, 900
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    # 2. የሚያምር የዳር መስመር (Border)
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#2C3E50", width=3)
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline="#BDC3C7", width=1)
    
    # 3. የአማርኛ ፎንት መጫን
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "AbyssinicaSIL-Regular.ttf")
    
    if os.path.exists(font_path):
        title_font = ImageFont.truetype(font_path, 34)
        body_font = ImageFont.truetype(font_path, 20)
        bold_font = ImageFont.truetype(font_path, 22)
    else:
        title_font = ImageFont.load_default(size=28)
        body_font = ImageFont.load_default(size=18)
        bold_font = ImageFont.load_default(size=20)

    # 4. የራስጌ ጽሑፍ (Header - Center Aligned)
    draw.text((width/2, 60), "ETHIO SHOE STORE", fill="#2C3E50", font=title_font, anchor="mm")
    draw.text((width/2, 100), "Official Payment Receipt / የክፍያ ማረጋገጫ ደረሰኝ", fill="#7F8C8D", font=body_font, anchor="mm")
    
    draw.line([(40, 130), (width - 40, 130)], fill="#BDC3C7", width=2)
    
    # 5. የትዕዛዝ መረጃዎች (Justified - የግራ ርዕስ በ50px፣ የቀኝ መረጃ በ580px በቀኝ በኩል እኩል እንዲሰለፉ)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    info_data = [
        ("Order ID / የትዕዛዝ ቁጥር:", f"#ETH-{order_id}", True),
        ("Date / ቀን:", current_date, False),
        ("Customer / ደንበኛ:", user_name, False),
        ("Phone / ስልክ ቁጥር:", phone, False),
    ]
    
    y_offset = 160
    for label, value, is_bold in info_data:
        fnt = bold_font if is_bold else body_font
        clr = "#2C3E50" if is_bold else "#34495E"
        # የግራ አሰላለፍ (Left Aligned)
        draw.text((50, y_offset), label, fill="#7F8C8D", font=body_font)
        # የቀኝ አሰላለፍ (Right Aligned - anchor="ra")
        draw.text((580, y_offset), str(value), fill=clr, font=fnt, anchor="ra")
        y_offset += 45
        
    draw.line([(40, y_offset + 10), (width - 40, y_offset + 10)], fill="#BDC3C7", width=2)
    
    # 6. የእቃው ዝርዝር (Justified)
    y_offset += 40
    draw.text((50, y_offset), "Order Items / የዕቃው ዝርዝር", fill="#2C3E50", font=bold_font)
    
    y_offset += 50
    draw.text((50, y_offset), f"Item / ጫማ: {product_name}", fill="#34495E", font=body_font)
    draw.text((580, y_offset), f"Size / ሳይዝ: {size}", fill="#34495E", font=body_font, anchor="ra")
    
    # የዋጋ ማጠቃለያ ሳጥን (Total Box)
    y_offset += 70
    draw.rectangle([(40, y_offset), (width - 40, y_offset + 60)], fill="#F8F9F9", outline="#BDC3C7")
    draw.text((60, y_offset + 18), "Total Amount / ጠቅላላ ክፍያ:", fill="#2C3E50", font=bold_font)
    draw.text((570, y_offset + 18), f"{price} ETB", fill="#E74C3C", font=bold_font, anchor="ra")
    
    # 7. የግርጌ ማስታወሻ (Footer - አድሚኑ ክፍያውን ካረጋገጠ በኋላ የሚላክ የመጨረሻ ጽሑፍ)
    y_offset += 140
    draw.text((width/2, y_offset), "This receipt confirms that your payment has been successfully processed.", fill="#7F8C8D", font=body_font, anchor="mm")
    draw.text((width/2, y_offset + 35), "ይህ ደረሰኝ ክፍያዎ በተሳካ ሁኔታ መጠናቀቁን ያረጋግጣል።", fill="#7F8C8D", font=body_font, anchor="mm")
    draw.text((width/2, y_offset + 80), "Thank you for shopping with us! / እናመሰግናለን!", fill="#2C3E50", font=bold_font, anchor="mm")
    
    filename = f"receipt_{order_id}.png"
    image.save(filename)
    return filename