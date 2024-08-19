import json
from pathlib import Path
from loguru import logger

class Config:
    def __init__(self, config_path: Path | str):
        self.config_path = config_path if isinstance(config_path, Path) else Path(config_path)
        
        self.game_install_dir = None
        self.selected_binary = None
        self.particles_disabled = False

    def exists(self):
        exists = self.config_path.exists()
        logger.debug(f"Config exists: {exists}")
        return exists
        
    def valid(self):
        logger.debug("Checking if config is valid")
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            valid = 'game_install_dir' in config and Path(config['game_install_dir']).exists()
            logger.debug(f"Config valid: {valid}")
            return valid
        except Exception as e:
            logger.exception(f"Error in config_valid: {e}")
            return False

    def save(self):
        config = {
            'game_install_dir': str(self.game_install_dir),
            'selected_binary': self.selected_binary,
            'particles_disabled': self.particles_disabled
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        logger.debug(f"Config saved: {config}")

    def load(self):
        if not self.exists():
            logger.warning("Config file does not exist")
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.game_install_dir = Path(config.get('game_install_dir'))
            self.selected_binary = config.get('selected_binary')
            self.particles_disabled = config.get('particles_disabled', False)
            logger.debug(f"Config loaded - Game install directory: {self.game_install_dir}")
            logger.debug(f"Config loaded - Selected binary: {self.selected_binary}")
            logger.debug(f"Config loaded - Particles disabled: {self.particles_disabled}")
            return True
        except Exception as e:
            logger.exception(f"Error loading config: {e}")
            return False