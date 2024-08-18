import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_path: Path | str):
        self.config_path = config_path if isinstance(config_path, Path) else Path(config_path)
        
        self.game_install_dir = None
        self.selected_binary = None

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
        config = {'game_install_dir': self.game_install_dir, 'selected_binary': self.selected_binary}
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def load(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        self.game_install_dir = config.get('game_install_dir')
        self.selected_binary = config.get('selected_binary')
        logger.debug(f"Game install directory: {self.game_install_dir}")
        logger.debug(f"Selected binary: {self.selected_binary}")
