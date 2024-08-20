import pathlib
import win32gui
import win32ui
import win32con
from PIL import Image

def get_exe_icon(exe_path: pathlib.Path):
    # Ensure the path is absolute and exists
    exe_path = exe_path.resolve()
    if not exe_path.exists() or exe_path.suffix.lower() != '.exe':
        raise ValueError("The provided path must be an existing .exe file")

    # Load the icon
    ico_x = win32gui.ExtractIcon(0, str(exe_path), 0)
    if ico_x == 0:
        raise RuntimeError(f"Could not extract icon from {exe_path}")

    # Get icon dimensions
    icon_info = win32gui.GetIconInfo(ico_x)
    icon_bmp = icon_info[3]  # hbmColor
    if icon_bmp == 0:  # If hbmColor is NULL, use hbmMask
        icon_bmp = icon_info[4]
    bmp_info = win32gui.GetObject(icon_bmp)
    icon_width, icon_height = bmp_info.bmWidth, bmp_info.bmHeight

    # Create a device context and bitmap
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, icon_width, icon_height)
    hdc = hdc.CreateCompatibleDC()

    # Draw the icon onto the bitmap
    hdc.SelectObject(hbmp)
    win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, ico_x, icon_width, icon_height, 0, None, win32con.DI_NORMAL)

    # Convert bitmap to bytes
    bmpstr = hbmp.GetBitmapBits(True)

    # Create PIL Image
    icon_image = Image.frombuffer(
        'RGBA',
        (icon_width, icon_height),
        bmpstr, 'raw', 'BGRA', 0, 1
    )

    # Clean up
    win32gui.DestroyIcon(ico_x)
    hdc.DeleteDC()
    win32gui.ReleaseDC(0, hdc.GetHandleOutput())
    win32gui.DeleteObject(hbmp.GetHandle())

    return icon_image


if __name__ == "__main__":
    exe_path = pathlib.Path("C:/Windows/System32/notepad.exe")
    icon = get_exe_icon(exe_path)
    icon.show()