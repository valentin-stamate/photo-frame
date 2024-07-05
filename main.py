import os
from PIL import Image, ImageDraw

SQUARE = (1080, 1080)    # 1 / 1
PORTRAIT = (1080, 1350)  # 4 / 5
LANDSCAPE = (1080, 566)  # 1.91 / 1
FRAME_COLOR = (255, 255, 255)
FRAME_PADDING = 64
RADIUS = 32

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def visit(image_path: str):
    name, extension = os.path.splitext(os.path.basename(image_path))
    export_path = os.path.join('export', f'{name}.png')

    with Image.open(image_path) as image:

        if image.width == image.height:
            final_image = Image.new('RGBA', SQUARE, FRAME_COLOR)
            resize_width = final_image.width - FRAME_PADDING * 2
            resize_height = resize_width * image.height // image.width

        if image.width < image.height:
            final_image = Image.new('RGBA', PORTRAIT, FRAME_COLOR)
            resize_height = final_image.height - FRAME_PADDING * 2
            resize_width = resize_height * image.width // image.height

        if image.width > image.height:
            final_image = Image.new('RGBA', SQUARE, FRAME_COLOR)
            resize_width = final_image.width - FRAME_PADDING * 2
            resize_height = resize_width * image.height // image.width

        image = image.convert('RGBA')
        image = image.resize((resize_width, resize_height))

        if RADIUS != 0:
            image = add_corners(image, RADIUS)

        position = (- (image.width - final_image.width) // 2, - (image.height - final_image.height) // 2)

        final_image.paste(image, position, mask=image)
        final_image.save(export_path, format='PNG', quality=100)

        print(f'Done {export_path}')


def change_recursive(root: str):
    dir_list = os.listdir(root)

    for d in dir_list:
        if d == '.gitkeep':
            continue

        file_or_dir = os.path.join(root, d)

        if os.path.isfile(file_or_dir):
            visit(file_or_dir)


def main():
    change_recursive('data')


if __name__ == '__main__':
    main()
