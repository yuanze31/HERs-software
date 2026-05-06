import os
from PIL import Image, ImageSequence


def resize_image(image, target_width):
    w, h = image.size
    if w == target_width:
        return image
    new_height = int(h * target_width / w)
    return image.resize((target_width, new_height), Image.LANCZOS)


def process_file(input_path, output_path, target_width):
    img = None
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        img = Image.open(input_path)
        original_format = img.format.upper() if img.format else None

        if getattr(img, 'is_animated', False) and original_format in ('GIF', 'WEBP'):
            frames = []
            durations = []
            disposals = []
            transparency = img.info.get('transparency', None)
            background = img.info.get('background', None)

            for i, frame in enumerate(ImageSequence.Iterator(img)):
                frame_rgba = frame.convert('RGBA')
                resized_frame = resize_image(frame_rgba, target_width)
                frames.append(resized_frame)
                durations.append(frame.info.get('duration', 100))
                disposals.append(frame.disposal_method if hasattr(frame, 'disposal_method') else 1)

            save_args = {
                'format': original_format,
                'save_all': True,
                'append_images': frames[1:],
                'duration': durations,
                'loop': img.info.get('loop', 0),
                'disposal': disposals,
            }

            if transparency is not None:
                save_args['transparency'] = transparency
            if background is not None:
                save_args['background'] = background

            frames[0].save(output_path, **save_args)

        else:
            output_format = 'JPEG' if original_format in ('JPEG', 'JFIF') else original_format

            if output_format == 'JPEG':
                resized_img = resize_image(img.convert('RGB'), target_width)
            else:
                resized_img = resize_image(img.convert('RGBA'), target_width)

            save_args = {'format': output_format}
            if output_format == 'JPEG':
                save_args['quality'] = 100
            resized_img.save(output_path, **save_args)

        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if img:
            img.close()


def should_exclude_dir(dir_name):
    return dir_name.startswith('output_') and dir_name[7:].isdigit()


class ImageResizer:
    def __init__(self):
        self.valid_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.jfif'}

    def process_images(self, current_dir, target_width, progress_callback=None):
        output_dir_name = f"output_{target_width}"
        output_dir = os.path.join(current_dir, output_dir_name)
        os.makedirs(output_dir, exist_ok=True)

        image_files = []

        for root, dirs, files in os.walk(current_dir):
            dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.valid_exts:
                    input_path = os.path.join(root, file)
                    rel_path = os.path.relpath(input_path, current_dir)
                    output_path = os.path.join(output_dir, rel_path)
                    image_files.append((input_path, output_path))

        total_count = len(image_files)
        if total_count == 0:
            return {'success': False, 'message': "未找到任何图像文件"}

        processed_count = 0
        errors = []

        for i, (input_path, output_path) in enumerate(image_files, 1):
            success, error = process_file(input_path, output_path, target_width)
            if success:
                processed_count += 1
            else:
                errors.append(f"处理失败 [{i}/{total_count}]: {os.path.basename(input_path)} - {error}")

            if progress_callback:
                progress_callback(i, total_count, processed_count)

        result = {
            'success': True,
            'total': total_count,
            'processed_count': processed_count,
            'output_dir': output_dir,
            'errors': errors
        }
        return result