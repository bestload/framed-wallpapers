import os
import csv
from PIL import Image, ImageDraw, ImageFont

def process_images_with_captions(input_dir, csv_path, output_dir, target_size=(1920, 1080), font_size=30, padding=10, scale_factor=0.9):
    """
    Обрабатывает все изображения (.jpg, .jpeg) в директории: уменьшает с сохранением пропорций,
    центрирует на черном фоне 1920x1080, добавляет деревянную рамку и подпись из CSV-файла.

    Args:
        input_dir (str): Путь к директории с изображениями.
        csv_path (str): Путь к CSV-файлу с подписями.
        output_dir (str): Путь к директории для сохранения результатов.
        target_size (tuple): Целевой размер холста (ширина, высота) (по умолчанию 1920x1080).
        font_size (int): Размер шрифта (по умолчанию 30).
        padding (int): Отступ для текста и рамки (по умолчанию 10 пикселей).
        scale_factor (float): Коэффициент уменьшения изображения (0.9 = 90% от максимального размера).
    """
    try:
        # Проверяем существование директорий
        if not os.path.isdir(input_dir):
            raise FileNotFoundError(f"Директория {input_dir} не найдена.")
        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"CSV-файл {csv_path} не найден.")
        os.makedirs(output_dir, exist_ok=True)

        # Читаем CSV-файл
        captions = []
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'caption' not in reader.fieldnames:
                raise ValueError("CSV-файл должен содержать столбец 'caption'.")
            captions = [row['caption'] for row in reader]

        # Получаем список изображений (.jpg, .jpeg)
        image_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg'))])

        # Проверяем соответствие количества изображений и подписей
        if len(image_files) != len(captions):
            print(f"Предупреждение: Количество изображений ({len(image_files)}) не совпадает с количеством подписей ({len(captions)}).")

        # Загружаем шрифт (для Ubuntu)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
                print("Стандартные шрифты не найдены, используется дефолтный.")

        # Обрабатываем каждое изображение
        for idx, image_file in enumerate(image_files):
            try:
                # Открываем изображение
                image_path = os.path.join(input_dir, image_file)
                image = Image.open(image_path)

                # Вычисляем максимальный размер изображения с учетом текста и рамки
                max_image_height = target_size[1] - font_size - 2 * padding
                max_image_width = target_size[0] - 2 * padding
                max_image_width = int(max_image_width * scale_factor)
                max_image_height = int(max_image_height * scale_factor)

                # Уменьшаем изображение с сохранением пропорций
                image.thumbnail((max_image_width, max_image_height), Image.Resampling.LANCZOS)

                # Создаем новое изображение 1920x1080 с черным фоном
                new_image = Image.new('RGB', target_size, (0, 0, 0))

                # Вычисляем позицию для центрирования изображения
                offset = ((target_size[0] - image.size[0]) // 2,
                          (target_size[1] - image.size[1] - font_size - 2 * padding) // 2)

                # Создаем объект для рисования
                draw = ImageDraw.Draw(new_image)

                # Создаем деревянную рамку
                frame_thickness = 20
                frame_color_light = (139, 69, 19)  # Светло-коричневый
                frame_color_dark = (92, 51, 23)   # Темно-коричневый
                frame_left = offset[0] - frame_thickness
                frame_top = offset[1] - frame_thickness
                frame_right = offset[0] + image.size[0] + frame_thickness
                frame_bottom = offset[1] + image.size[1] + frame_thickness

                # Рисуем рамку
                draw.rectangle((frame_left, frame_top, frame_right, frame_bottom), fill=frame_color_light)
                draw.rectangle(
                    (frame_left + frame_thickness // 2, frame_top + frame_thickness // 2,
                     frame_right - frame_thickness // 2, frame_bottom - frame_thickness // 2),
                    fill=frame_color_dark
                )

                # Вставляем уменьшенное изображение
                new_image.paste(image, offset)

                # Получаем подпись из CSV (если есть)
                caption = captions[idx] if idx < len(captions) else f"Без подписи (изображение {idx + 1})"

                # Вычисляем размер текста
                text_bbox = draw.textbbox((0, 0), caption, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Вычисляем координаты для текста (центрировано под изображением)
                x = (target_size[0] - text_width) // 2
                y = offset[1] + image.size[1] + padding + 30;

                # Добавляем белый текст
                draw.text((x, y), caption, font=font, fill=(255, 255, 255))

                # Сохраняем изображение
                output_path = os.path.join(output_dir, f"processed_{image_file}")
                new_image.save(output_path, "JPEG")
                print(f"Обработано: {image_file} -> {output_path}")

            except Exception as e:
                print(f"Ошибка при обработке {image_file}: {e}")

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Пример использования
if __name__ == "__main__":
    # Входные параметры
    input_dir = "input"       # Путь к директории с изображениями
    csv_path = "captions.csv"   # Путь к CSV-файлу
    output_dir = "output"       # Путь к директории для результатов
    scale_factor = 0.8          # Дополнительное уменьшение на 10%

    # Вызов функции
    process_images_with_captions(input_dir, csv_path, output_dir, font_size=30, padding=10, scale_factor=scale_factor)