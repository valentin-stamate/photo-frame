import os
from PIL import Image, ImageDraw

SQUARE = (1080, 1080)    # 1 / 1
PORTRAIT = (1080, 1350)  # 4 / 5
LANDSCAPE = (1080, 566)  # 1.91 / 1
FRAME_COLOR = (255, 255, 255)
FRAME_PADDING = 64
RADIUS = 24


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


# Places the image into a white background together with padding
def change_with_frame(image_path: str):
    name, extension = os.path.splitext(os.path.basename(image_path))
    export_path = os.path.join('export', f'{name}.jpg')

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
        final_image = final_image.convert('RGB')

        exif_info = image.info['exif']
        final_image.save(export_path, format='JPEG', quality=100, exif=exif_info)

        print(f'Done {export_path}')


# Resize and crop the photo specific to instagram format
def change_full(image_path: str):
    name, extension = os.path.splitext(os.path.basename(image_path))
    export_path = os.path.join('export', f'{name}.jpg')
    export_path_square = os.path.join('export', f'{name}_sq.jpg')

    with Image.open(image_path) as image:

        img_aspect = image.width / image.height
        make_square = False

        if image.width < image.height:
            size = PORTRAIT
            target_aspect = PORTRAIT[0] / PORTRAIT[1]

        if image.width > image.height:
            size = LANDSCAPE
            target_aspect = LANDSCAPE[0] / LANDSCAPE[1]
            make_square = True

        if image.width == image.height:
            size = SQUARE
            target_aspect = 1

        if target_aspect > img_aspect:
            new_height = int(size[0] / img_aspect)
            img = image.resize((size[0], new_height))

            top = (new_height - size[1]) // 2
            img = img.crop((0, top, size[0], top + size[1]))
        else:
            new_width = int(size[1] * img_aspect)
            img = image.resize((new_width, size[1]))

            left = (new_width - size[0]) // 2
            img = img.crop((left, 0, left + size[0], size[1]))

        exif_info = image.info['exif']
        img.save(export_path, format='JPEG', quality=100, exif=exif_info)

        if make_square:
            top = (image.width - image.height) // 2
            squared_image = image.crop((top, 0, top + image.height, image.height))

            squared_image = squared_image.resize(SQUARE)

            exif_info = image.info['exif']
            squared_image.save(export_path_square, format='JPEG', quality=100, exif=exif_info)

        print(f'Done {export_path}')


def change_recursive(root: str, visit):
    dir_list = os.listdir(root)

    for d in dir_list:
        if d == '.gitkeep':
            continue

        file_or_dir = os.path.join(root, d)

        if os.path.isfile(file_or_dir):
            visit(file_or_dir)


def main():
    change_recursive('data', change_full)


if __name__ == '__main__':
    main()
