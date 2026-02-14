import subprocess
import re
from screeninfo import get_monitors

def get_screen_resolution_screeninfo():
    """
    Получает разрешение экрана с использованием библиотеки screeninfo.
    Возвращает список кортежей (ширина, высота) для всех мониторов.
    """
    try:
        resolutions = []
        for monitor in get_monitors():
            resolutions.append((monitor.width, monitor.height))
        return resolutions
    except Exception as e:
        print(f"Ошибка screeninfo: {e}")
        return None

def get_screen_resolution_xrandr():
    """
    Получает разрешение экрана с использованием xrandr (для X11).
    Возвращает список кортежей (ширина, высота) для активных дисплеев.
    """
    try:
        result = subprocess.run(['xrandr'], capture_output=True, text=True, check=True)
        output = result.stdout
        # Ищем строки с текущим разрешением (содержат '*')
        pattern = re.compile(r'(\d+x\d+)\s+\d+\.\d+\*')
        resolutions = []
        for match in pattern.finditer(output):
            width, height = map(int, match.group(1).split('x'))
            resolutions.append((width, height))
        return resolutions
    except subprocess.CalledProcessError:
        print("Ошибка: xrandr не удалось выполнить. Возможно, используется Wayland.")
        return None
    except Exception as e:
        print(f"Ошибка xrandr: {e}")
        return None

def get_screen_resolution_xdpyinfo():
    """
    Получает разрешение экрана с использованием xdpyinfo (для X11).
    Возвращает кортеж (ширина, высота) для основного дисплея.
    """
    try:
        result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, check=True)
        output = result.stdout
        pattern = re.compile(r'dimensions:\s+(\d+)x(\d+)\s+pixels')
        match = pattern.search(output)
        if match:
            width, height = map(int, match.groups())
            return [(width, height)]
        return None
    except subprocess.CalledProcessError:
        print("Ошибка: xdpyinfo не удалось выполнить. Возможно, используется Wayland.")
        return None
    except Exception as e:
        print(f"Ошибка xdpyinfo: {e}")
        return None

def main():
    print("Получение разрешения экрана...")
    
    # Попробуем screeninfo
    print("\nМетод 1: screeninfo")
    resolutions = get_screen_resolution_screeninfo()
    if resolutions:
        for i, (width, height) in enumerate(resolutions, 1):
            print(f"Монитор {i}: {width}x{height}")
    else:
        print("Не удалось получить разрешение через screeninfo.")

    # Попробуем xrandr (только для X11)
    print("\nМетод 2: xrandr")
    resolutions = get_screen_resolution_xrandr()
    if resolutions:
        for i, (width, height) in enumerate(resolutions, 1):
            print(f"Монитор {i}: {width}x{height}")
    else:
        print("Не удалось получить разрешение через xrandr.")

    # Попробуем xdpyinfo (только для X11)
    print("\nМетод 3: xdpyinfo")
    resolutions = get_screen_resolution_xdpyinfo()
    if resolutions:
        for i, (width, height) in enumerate(resolutions, 1):
            print(f"Монитор {i}: {width}x{height}")
    else:
        print("Не удалось получить разрешение через xdpyinfo.")

if __name__ == "__main__":
    main()