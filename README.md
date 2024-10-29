# TurtleLauncher

A modern, feature-rich launcher for Turtle WoW built with Python and Qt (PySide6).

## Features

### Core Functionality
- **Game Management**
  - Download and install Turtle WoW client
  - Launch multiple game binaries (WoW.exe, WoW_tweaked.exe, etc.)
  - Automatic game version detection
  - Clear cache and addon settings
  - Monitor game process status

### User Interface
- **Modern Design**
  - Semi-transparent, modern UI with gradient effects
  - Animated progress bar with particle effects
  - Responsive layout that adapts to window size
  - System tray integration
  - Multi-language support

### Content Integration
- **Social Features**
  - Twitter feed integration
  - Discord community link
  - Turtle TV video player
  - Featured content display

### Advanced Features
- **Addon Management**
  - Browse and manage addons
  - Enable/disable addons
  - Categorize addons
  - Update notifications

### Quality of Life
- **Settings & Customization**
  - Configurable particle effects
  - Launch options (minimize on launch, clear cache)
  - Binary selection for different game versions
  - Multiple display languages

### Game Fixes
- Black screen fix
- VanillaTweaks Alt-Tab fix
- Various performance optimizations

## Technical Requirements

### Dependencies
```toml
[tool.poetry.dependencies]
python = ">=3.10,<3.13"
pywin32 = "^306"
pyside6 = {extras = ["multimedia"], version = "^6.7.2"}
httpx = {extras = ["http2"], version = "^0.27.0"}
loguru = "^0.7.2"
pillow = "^10.4.0"
cloudscraper = "^1.2.71"
opencv-python = "^4.10.0.84"
pyside6-addons = "^6.7.2"
pyside6-essentials = "^6.7.2"
```

## Installation

1. **Using Poetry (Recommended)**
   ```bash
   poetry install
   ```

## Configuration

The launcher stores its configuration in `%USERPROFILE%/Documents/TurtleLauncher/launcher.json` with the following settings:
- Game installation directory
- Selected binary
- UI preferences
- Language settings
- Launch options

## Development

### Building from Source
1. Clone the repository
   ```bash
   git clone https://github.com/Aareon/TurtleLauncher.git
   cd TurtleLauncher
   ```

2. Install dependencies
   ```bash
   poetry install
   ```

3. Run the launcher
   ```bash
   poetry run python -m turtlelauncher
   ```

### Logging

The launcher uses the `loguru` library for logging. Logs are stored in:
```
%USERPROFILE%/Documents/TurtleLauncher/logs/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Links
- [Turtle WoW Website](https://turtle-wow.org/)
- [Discord Community](https://discord.gg/turtlewow)
- [GitHub Repository](https://github.com/Aareon/TurtleLauncher)

## Support

For support, join the Discord community or open an issue on GitHub.