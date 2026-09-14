import os
import re

from PIL import Image


def get_number_suffix(string: str) -> int:
    num = 0
    order = 0
    for char in reversed(string):
        if char.isdigit():
            num = num + int(char) * pow(10, order)
            order += 1
        else:
            break
    return num


def remove_right_whitespace(image_path, tolerance=10):
    """
    Remove whitespace from the right side of an image.

    Args:
        image_path: Path to the input image
        tolerance: How much variation from white to consider as whitespace (0-255)
    """
    # Open the image
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size

    # Start from the right edge and move left
    right_most_non_white = width - 1

    for x in range(width - 1, -1, -1):
        has_content = False
        for y in range(height - 1):
            r, g, b = pixels[x, y][:3]  # Get RGB values
            # Check if pixel is not white (within tolerance)
            if (
                abs(r - 255) > tolerance
                or abs(g - 255) > tolerance
                or abs(b - 255) > tolerance
            ):
                has_content = True
                break

        if has_content:
            right_most_non_white = x
            break

    # If we found content, crop the image
    if right_most_non_white < width - 1:
        # Add a small padding (optional) - adjust as needed
        padding = 5
        crop_width = right_most_non_white + padding + 1
        cropped = img.crop((0, 0, crop_width, height))
        cropped.save(image_path)


class WindowsPath:
    def __init__(self, path: str):
        self.windows_path = WindowsPath._to_windows_path(path)
        self.wsl_path = WindowsPath._to_wsl_path(path)

    def _to_windows_path(wsl_path: str) -> str:
        """Converts WSL path to Windows path. If path is already Windows, it will not be changed."""
        if not wsl_path.startswith("/mnt"):
            return wsl_path

        # Remove /mnt/ and replace forward slashes with backslashes
        path = wsl_path.removeprefix("/mnt/").replace("/", "\\")

        # Handle drive letter (c -> C:)
        def replace_drive(match):
            drive = match.group(1).upper()
            return f"{drive}:"

        # Convert "c" to "C:"
        path = re.sub(r"^([A-Za-z])", replace_drive, path)

        return path

    def _to_wsl_path(windows_path: str) -> str:
        """Converts path to Linux-style path. If path is already Linux-style, it will not be changed."""
        # Replace backslashes with forward slashes
        path = windows_path.replace("\\", "/")

        # Handle drive letter (C:\ -> /mnt/c/)
        def replace_drive(match):
            drive = match.group(1).lower()
            return f"/mnt/{drive}/"

        # Convert "C:/" to "/mnt/c/"
        path = re.sub(r"^([A-Za-z]):/", replace_drive, path)

        return path

    def basename(self) -> str:
        return os.path.basename(self.wsl_path)

    def join(self, path: str) -> "WindowsPath":
        # Replace backslashes with forward slashes
        path = path.replace("\\", "/").lstrip("/")

        return WindowsPath(self.wsl_path + "/" + path)
