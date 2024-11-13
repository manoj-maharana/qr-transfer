from heic2png import HEIC2PNG

def transform_heic_to_png(heic_path):
    image = HEIC2PNG(heic_path, quality=85)
    png_path = heic_path.replace('.heic', '.png')
    image.save(png_path)
    return png_path
