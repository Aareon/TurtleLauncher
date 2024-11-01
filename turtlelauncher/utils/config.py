import json
from pathlib import Path
from loguru import logger


class Config:
    def __init__(self, config_path: Path | str):
        self.config_path = config_path if isinstance(config_path, Path) else Path(config_path)
        
        self.game_install_dir = None
        self.selected_binary = None
        self.particles_disabled = False
        self.transparency_disabled = False
        self.minimize_on_launch = False
        self.clear_cache_on_launch = False
        self.language = "English"

        self._loaded = False

        if self.exists():
            self.load()

    def exists(self):
        exists = self.config_path.exists()
        logger.debug(f"Config exists: {exists}")
        return exists
        
    def valid(self):
        logger.debug("Checking if config is valid")
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            if 'game_install_dir' not in config:
                logger.warning("'game_install_dir' not found in config")
                return False
            
            if config['game_install_dir'] is None:
                logger.warning("'game_install_dir' is None")
                return False
            
            install_dir = Path(config['game_install_dir'])
            if not install_dir.exists():
                logger.warning(f"Game install directory does not exist: {install_dir}")
                return False
            
            logger.debug(f"Config valid. Game install directory: {install_dir}")
            return True
        except Exception as e:
            logger.exception(f"Error in config_valid: {e}")
            return False

    def save(self):
        config = {
            'game_install_dir': str(self.game_install_dir) if self.game_install_dir else None,
            'selected_binary': self.selected_binary,
            'particles_disabled': self.particles_disabled,
            'transparency_disabled': self.transparency_disabled,
            'minimize_on_launch': self.minimize_on_launch,
            'clear_cache_on_launch': self.clear_cache_on_launch,
            'language': self.language
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
            self.game_install_dir = Path(config['game_install_dir']) if config.get('game_install_dir') else None
            self.selected_binary = config.get('selected_binary')
            self.particles_disabled = config.get('particles_disabled', False)
            self.transparency_disabled = config.get('transparency_disabled', False)
            self.minimize_on_launch = config.get('minimize_on_launch', False)
            self.clear_cache_on_launch = config.get('clear_cache_on_launch', False)
            self.language = config.get('language', 'English')
            logger.debug(f"Config loaded - Game install directory: {self.game_install_dir}")
            logger.debug(f"Config loaded - Selected binary: {self.selected_binary}")
            logger.debug(f"Config loaded - Particles disabled: {self.particles_disabled}")
            logger.debug(f"Config loaded - Transparency disabled: {self.transparency_disabled}")
            logger.debug(f"Config loaded - Minimize on launch: {self.minimize_on_launch}")
            logger.debug(f"Config loaded - Clear cache on launch: {self.clear_cache_on_launch}")
            logger.debug(f"Config loaded - Language: {self.language}")
            self._loaded = True
            return True
        except Exception as e:
            logger.exception(f"Error loading config: {e}")
            return False