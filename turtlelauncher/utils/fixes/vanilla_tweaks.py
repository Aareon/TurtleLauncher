import re
from pathlib import Path
from loguru import logger
from turtlelauncher.dialogs.error import ErrorDialog
from turtlelauncher.dialogs import show_success_dialog


def fix_alt_tab(game_install_dir: Path):
    dxvk_conf_path = Path(game_install_dir) / "dxvk.conf"

    if not dxvk_conf_path.exists():
        error_message = "dxvk.conf file not found. Unable to apply VanillaTweaks Alt-Tab fix."
        logger.error(error_message)
        return "error", error_message

    try:
        with open(dxvk_conf_path, 'r') as file:
            dxvk_lines = file.readlines()

        dxvk_setting_found = False
        dxvk_modified = False
        dialog_mode_pattern = re.compile(r'^#?\s*d3d9\.enableDialogMode\s*=')

        for i, line in enumerate(dxvk_lines):
            if dialog_mode_pattern.match(line):
                dxvk_setting_found = True
                if '=' in line:
                    key, value = line.split('=')
                    if value.strip().lower() != 'true':
                        dxvk_lines[i] = 'd3d9.enableDialogMode = True\n'
                        dxvk_modified = True
                else:
                    dxvk_lines[i] = 'd3d9.enableDialogMode = True\n'
                    dxvk_modified = True
                break

        if not dxvk_setting_found:
            dxvk_lines.append('d3d9.enableDialogMode = True\n')
            dxvk_modified = True

        if dxvk_modified:
            with open(dxvk_conf_path, 'w') as file:
                file.writelines(dxvk_lines)
            logger.info("Successfully applied VanillaTweaks Alt-Tab fix")
            return "success", "VanillaTweaks Alt-Tab fix has been applied successfully."
        else:
            logger.info("VanillaTweaks Alt-Tab fix was already applied")
            return "warning", "VanillaTweaks Alt-Tab fix was already applied. No changes were needed."

    except Exception as e:
        error_message = f"An error occurred while applying VanillaTweaks Alt-Tab fix: {str(e)}"
        logger.error(error_message)
        return "error", error_message