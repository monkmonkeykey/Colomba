from PIL import Image, ImageSequence

gif_path = "kk.gif"
output_file = "kk.js"

OLED_W = 128
OLED_H = 64
THRESHOLD = 200

# velocidad del loop automático
LOOP_DELAY = 80


def frame_to_bw(frame):
    rgba = frame.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(bg, rgba).convert("L")
    return comp.point(lambda p: 1 if p < THRESHOLD else 0)


def bw_to_hlines(img_bw):
    runs = []
    for y in range(img_bw.height):
        x = 0
        while x < img_bw.width:
            while x < img_bw.width and img_bw.getpixel((x, y)) != 1:
                x += 1
            if x >= img_bw.width:
                break
            start = x
            while x < img_bw.width and img_bw.getpixel((x, y)) == 1:
                x += 1
            runs.append((y, start, x - start))
    return runs


img = Image.open(gif_path)

if img.size != (OLED_W, OLED_H):
    raise ValueError(f"El GIF debe medir exactamente {OLED_W}x{OLED_H}, pero mide {img.size}")

frames_runs = []
for frame in ImageSequence.Iterator(img):
    bw = frame_to_bw(frame)
    runs = bw_to_hlines(bw)
    frames_runs.append(runs)

lines = []

# Funciones por frame
for i, runs in enumerate(frames_runs):
    lines.append(f"function drawFrame{i}() {{")
    lines.append("    OLED12864_I2C.clear()")
    for y, x, length in runs:
        lines.append(f"    OLED12864_I2C.hline({x}, {y}, {length}, 1)")
    lines.append("    OLED12864_I2C.draw()")
    lines.append("}")
    lines.append("")

# Variables globales
lines.append("let currentFrame = 0")
lines.append("let lastFrameDrawn = -1")
lines.append("let isLooping = false")
lines.append(f"let totalFrames = {len(frames_runs)}")
lines.append("")

# Mostrar frame actual solo si cambió
lines.append("function showCurrentFrame() {")
lines.append("    if (currentFrame == lastFrameDrawn) {")
lines.append("        return")
lines.append("    }")
lines.append("")
lines.append("    if (currentFrame == 0) {")
lines.append("        drawFrame0()")
for i in range(1, len(frames_runs)):
    lines.append(f"    }} else if (currentFrame == {i}) {{")
    lines.append(f"        drawFrame{i}()")
lines.append("    }")
lines.append("")
lines.append("    lastFrameDrawn = currentFrame")
lines.append("}")
lines.append("")

# Inicialización
lines.append("OLED12864_I2C.init(60)")
lines.append("OLED12864_I2C.zoom(false)")
lines.append("OLED12864_I2C.clear()")
lines.append("OLED12864_I2C.draw()")
lines.append("showCurrentFrame()")
lines.append("")

# Botón A = frame anterior si no está en loop
lines.append("input.onButtonPressed(Button.A, function () {")
lines.append("    if (isLooping) {")
lines.append("        return")
lines.append("    }")
lines.append("    currentFrame += -1")
lines.append("    if (currentFrame < 0) {")
lines.append("        currentFrame = totalFrames - 1")
lines.append("    }")
lines.append("    showCurrentFrame()")
lines.append("})")
lines.append("")

# Botón B = frame siguiente si no está en loop
lines.append("input.onButtonPressed(Button.B, function () {")
lines.append("    if (isLooping) {")
lines.append("        return")
lines.append("    }")
lines.append("    currentFrame += 1")
lines.append("    if (currentFrame >= totalFrames) {")
lines.append("        currentFrame = 0")
lines.append("    }")
lines.append("    showCurrentFrame()")
lines.append("})")
lines.append("")

# Botón AB = alterna loop on/off
lines.append("input.onButtonPressed(Button.AB, function () {")
lines.append("    isLooping = !isLooping")
lines.append("})")
lines.append("")

# Loop automático desde el frame actual
lines.append("basic.forever(function () {")
lines.append("    if (isLooping) {")
lines.append("        currentFrame += 1")
lines.append("        if (currentFrame >= totalFrames) {")
lines.append("            currentFrame = 0")
lines.append("        }")
lines.append("        showCurrentFrame()")
lines.append(f"        basic.pause({LOOP_DELAY})")
lines.append("    } else {")
lines.append("        basic.pause(20)")
lines.append("    }")
lines.append("})")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Generado: {output_file}")