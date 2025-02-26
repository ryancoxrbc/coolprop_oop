# CoolProp Object-Oriented Wrapper

[![Python Package](https://github.com/ryancoxrbc/coolprop_oop/actions/workflows/python-package.yml/badge.svg)](https://github.com/ryancoxrbc/coolprop_oop/actions/workflows/python-package.yml)
[![Version](https://img.shields.io/pypi/v/coolprop-oop)](https://badge.fury.io/py/coolprop-oop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An object-oriented wrapper for CoolProp thermodynamic properties that makes working with thermodynamic states simpler and more intuitive.

## Features

- Object-oriented interface to CoolProp
- Easy access to common thermodynamic properties
- Support for humid air calculations via `StateHA`
- Support for pure fluid properties via `StatePROPS`
- Pythonic API that follows best practices

## Installation

```bash
pip install coolprop-oop
```

## Usage

### Humid Air Properties

```python
from coolprop_oop import StateHA

# Create a state for humid air
state = StateHA(['P', 101325, 'T', 293.15, 'R', 0.5])

# Access properties
print(f"Temperature: {state.tempc}°C")
print(f"Relative Humidity: {state.relhum * 100}%")
print(f"Humidity Ratio: {state.humrat} kg/kg")
print(f"Wet Bulb Temperature: {state.wetbulb - 273.15}°C")
print(f"Dew Point: {state.dewpoint - 273.15}°C")
```

### Pure Fluid Properties

```python
from coolprop_oop import StatePROPS

# Create a state for water
state = StatePROPS(['P', 101325, 'T', 373.15, 'water'])

# Access properties
print(f"Temperature: {state.tempc}°C")
print(f"Pressure: {state.press} Pa")
print(f"Density: {state.dens} kg/m³")
print(f"Enthalpy: {state.enthalpy} J/kg")
print(f"Entropy: {state.entropy} J/kg-K")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [CoolProp](http://www.coolprop.org/) for providing the underlying thermodynamic property calculations 