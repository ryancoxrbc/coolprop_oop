# CoolProp Object-Oriented Wrapper

[![Python Package](https://github.com/ryancoxrbc/coolprop_oop/actions/workflows/python-package.yml/badge.svg)](https://github.com/ryancoxrbc/coolprop_oop/actions/workflows/python-package.yml)
[![Version](https://img.shields.io/pypi/v/coolprop-oop)](https://badge.fury.io/py/coolprop-oop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An object-oriented wrapper for [CoolProp](http://www.coolprop.org/) thermodynamic properties. This library provides an intuitive, Pythonic interface to CoolProp's functionality for both humid air and pure fluid property calculations.

## Features

- **Object-oriented interface** to CoolProp's functionality
- **Property validation** to prevent physically impossible states
- **Automatic caching** of calculated properties for better performance
- Support for both **Humid Air** (`StateHA`) and **Pure Fluids** (`StatePROPS`)
- Comprehensive **state validation** with helpful error messages
- **Fully Pythonic API** with property-based getters and setters

## Installation

```bash
pip install coolprop-oop
```

## Usage

### Humid Air Properties

```python
from coolprop_oop import StateHA

# Create a state for humid air (OOP style, recommended)
state = StateHA()
state.tempc = 20      # Temperature in °C
state.press = 101325  # Pressure in Pa
state.relhum = 0.5    # Relative humidity (0-1)

# Access properties
print(f"Temperature: {state.tempc:.1f}°C")
print(f"Relative Humidity: {state.relhum * 100:.0f}%")
print(f"Humidity Ratio: {state.humrat:.6f} kg/kg")
print(f"Dew Point: {state.dewpoint - 273.15:.1f}°C")
print(f"Enthalpy: {state.enthalpy:.1f} J/kg")
print(f"Density: {state.density:.4f} kg/m³")

# Check which properties are currently constraining the state
print(f"Constraints: {state.constraints}")  # ['press', 'relhum', 'tempc']
```

### Pure Fluid Properties

```python
from coolprop_oop import StatePROPS

# Create a state for water (OOP style, recommended)
state = StatePROPS(fluid='Water')  # Set fluid first
state.tempc = 100     # Temperature in °C
state.press = 101325  # Pressure in Pa

# Access properties
print(f"Temperature: {state.tempc:.1f}°C")
print(f"Pressure: {state.press/1000:.2f} kPa")
print(f"Density: {state.dens:.2f} kg/m³")
print(f"Enthalpy: {state.enthalpy:.1f} J/kg")
print(f"Quality: {state.quality}")  # None if not in two-phase region

# Get extensive state information
constraints = state.constraints
print(f"Fluid state: {constraints['status']}")  # e.g., 'liquid', 'gas', 'two_phase'
print(f"Set properties: {', '.join(constraints['properties'])}")
```

### Error Handling and Validation

The library automatically validates inputs to prevent physically impossible states:

```python
try:
    state = StateHA()
    state.tempc = -300  # Below absolute zero
except ValueError as e:
    print(f"Error: {e}")  # "Error: Temperature cannot be below absolute zero"
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