import win32api

def get_file_version(file_path):
    try:
        # Get file information
        info = win32api.GetFileVersionInfo(file_path, "\\")
        
        # Get the file version
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        
        # Extract version numbers
        version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
        
        return version
    except Exception as e:
        return f"Error: {str(e)}"
