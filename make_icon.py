from PIL import Image, ImageDraw, ImageFilter

N = 256
img = Image.new("RGBA", (N, N), (6, 10, 19, 255))
d = ImageDraw.Draw(img)
d.rounded_rectangle((10, 10, 246, 246), radius=44, fill=(10, 16, 30, 255), outline=(44, 63, 90, 255), width=3)

glow = Image.new("RGBA", (N, N), (0, 0, 0, 0))
g = ImageDraw.Draw(glow)
box = (63, 63, 193, 193)
for start, end, color in [
    (-90, 25, (0, 220, 255, 255)),
    (30, 145, (255, 50, 210, 255)),
    (150, 265, (255, 220, 35, 255)),
]:
    g.arc(box, start=start, end=end, fill=color, width=8)

for coords, color in [
    ((128, 45, 128, 96), (0, 220, 255, 255)),
    ((160, 128, 211, 128), (255, 50, 210, 255)),
    ((128, 160, 128, 211), (255, 220, 35, 255)),
    ((45, 128, 96, 128), (0, 255, 170, 255)),
]:
    g.line(coords, fill=color, width=7)

g.polygon([(128, 104), (152, 128), (128, 152), (104, 128)], outline=(238, 247, 255, 255), width=5)
g.ellipse((122, 122, 134, 134), fill=(255, 255, 255, 255))

img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(8)))
img = Image.alpha_composite(img, glow)
img.save("crossaim_power.png", optimize=True)
img.save("crossaim_power.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print("Created crossaim_power.png and crossaim_power.ico")
