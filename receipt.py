# receipt.py
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def generate_receipt_image(order_id, user_name, product_name, price, size, phone):
    # 1. ንጹህ ነጭ ወረቀት ማዘጋጀት (ስፋት 600px፣ ቁመት 850px)
    width, height = 600, 850
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    # 2. የሚያምር የዳር መስመር (Border) መስራት
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#2C3E50", width=3)
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline="#BDC3C7", width=1)
    
    # 3. አማርኛ የሚደግፈውን AbyssinicaSIL ፎንት ከፕሮጀክቱ ማውጫ ላይ መጫን
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "AbyssinicaSIL-Regular.ttf")
    
    if os.path.exists(font_path):
        # Abyssinica ፎንት በባህሪው ትንሽ ረቀቅ ስላለ መጠኑን (Size) ከፍ አድርገነዋል
        title_font = ImageFont.truetype(font_path, 36)
        body_font = ImageFont.truetype(font_path, 22)
        bold_font = ImageFont.truetype(font_path, 24)
        print("✅ የአማርኛ ፎንት በተሳካ ሁኔታ ተገኝቷል!")
    else:
        # ⚠️ ፋይሉ በስህተት ካልተገኘ ቦቱ እንዳይበላሽ መከላከያ (ጽሑፉ ግን ሊያንስ ይችላል)
        print("⚠️ AbyssinicaSIL-Regular.ttf አልተገኘም! ወደ ዲፎልት ፎንት ተቀይሯል።")
        title_font = ImageFont.load_default(size=30)
        body_font = ImageFont.load_default(size=20)
        bold_font = ImageFont.load_default(size=22)

    # 4. የራስጌ ጽሑፍ (Header)
    draw.text((width/2, 60), "ETHIO SHOE STORE", fill="#2C3E50", font=title_font, anchor="mm")
    draw.text((width/2, 100), "Official Sales Receipt / የሽያጭ ማረጋገጫ", fill="#7F8C8D", font=body_font, anchor="mm")
    
    # የማስመሪያ መስመር (------)
    draw.line([(40, 130), (width - 40, 130)], fill="#BDC3C7", width=2)
    
    # 5. የትዕዛዝ መረጃዎች
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
        draw.text((50, y_offset), label, fill="#7F8C8D", font=body_font)
        draw.text((280, y_offset), str(value), fill=clr, font=fnt)
        y_offset += 42
        
    # ሌላ የማስመሪያ መስመር
    draw.line([(40, y_offset + 10), (width - 40, y_offset + 10)], fill="#BDC3C7", width=2)
    
    # 6. የእቃው ዝርዝር
    y_offset += 40
    draw.text((50, y_offset), "Order Items / የዕቃው ዝርዝር", fill="#2C3E50", font=bold_font)
    
    y_offset += 45
    draw.text((50, y_offset), f"Item / ጫማ: {product_name}", fill="#34495E", font=body_font)
    draw.text((450, y_offset), f"Size / ሳይዝ: {size}", fill="#34495E", font=body_font)
    
    # የዋጋ ማጠቃለያ ሳጥን (Total Box)
    y_offset += 70
    draw.rectangle([(40, y_offset), (width - 40, y_offset + 60)], fill="#F8F9F9", outline="#BDC3C7")
    draw.text((60, y_offset + 18), "Total Amount / ጠቅላላ ክፍያ:", fill="#2C3E50", font=bold_font)
    draw.text((420, y_offset + 18), f"{price} ETB", fill="#E74C3C", font=bold_font)
    
    # 7. የግርጌ ማስታወሻ (Footer)
    y_offset += 130
    draw.text((width/2, y_offset), "Please forward this receipt to the admin to confirm payment.", fill="#7F8C8D", font=body_font, anchor="mm")
    draw.text((width/2, y_offset + 35), "እባክዎ ይህንን ደረሰኝ ለባለቤቱ አስተላልፈው ክፍያ ይፈጽሙ።", fill="#7F8C8D", font=body_font, anchor="mm")
    draw.text((width/2, y_offset + 75), "Thank you for shopping with us! / እናመሰግናለን!", fill="#2C3E50", font=bold_font, anchor="mm")
    
    # 8. ፎቶውን ጊዚያዊ ቦታ ሴቭ አድርጎ መንገዱን መመለስ
    filename = f"receipt_{order_id}.png"
    image.save(filename)
    return filename