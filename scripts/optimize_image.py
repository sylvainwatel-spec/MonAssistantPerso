from PIL import Image
import os
import shutil

def optimize_image(image_path, target_width=1600):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.")
        return

    # Backup
    backup_path = image_path + ".bak"
    shutil.copy2(image_path, backup_path)
    print(f"Backed up original to {backup_path}")

    try:
        with Image.open(image_path) as img:
            print(f"Original size: {img.size}")
            
            # Convert to RGB (removes alpha)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > target_width:
                ratio = target_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized to: {img.size}")
            
            # Save as optimized PNG (to keep filename/code compat) or change to JPG
            # Since code uses specific filename, let's keep it but optimize
            # If we want to change format to JPG, we'd need to update code.
            # Let's stick to overwriting the PNG but ensuring it's RGB and optimized.
            # actually code loads it so format inside doesn't matter much if name matches.
            # But PNG compression can be slow. JPG is faster for photos.
            # Let's save as PNG for now to avoid code changes, but optimized.
            
            img.save(image_path, optimize=True, quality=85)
            print(f"Saved optimized image to {image_path}")
            
            original_size = os.path.getsize(backup_path)
            new_size = os.path.getsize(image_path)
            print(f"Size reduction: {original_size/1024:.2f}KB -> {new_size/1024:.2f}KB")

    except Exception as e:
        print(f"Error optimizing image: {e}")
        # Restore backup
        shutil.copy2(backup_path, image_path)
        print("Restored backup due to error.")

if __name__ == "__main__":
    optimize_image(r"c:\Users\sylva\.gemini\antigravity\scratch\simple_python_app\image\Page_accueil.png")
