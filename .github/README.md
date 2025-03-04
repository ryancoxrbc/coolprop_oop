# CoolProp Object-Oriented Wrapper

[![Python Package](https://github.com/ryancoxrbc/coolprop_oop/actions/workflows/python-package.yml/badge.svg)](https://github.com/ryancoxrbc/coolprop_oop/actions/workflows/python-package.yml)
[![Version](https://img.shields.io/pypi/v/coolprop-oop)](https://badge.fury.io/py/coolprop-oop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An object-oriented wrapper for CoolProp thermodynamic properties that makes working with thermodynamic states simpler and more intuitive.

## Features

- Object-oriented interface to CoolProp
- Simple property constraint management
- Support for humid air calculations via `StateHA`
- Support for pure fluid properties via `StateProps`
- Consistent SI unit system
- Compatible with CoolProp 6.7.0

## Installation

```bash
pip install coolprop-oop
```

## Usage

### Humid Air Properties

```python
from coolprop_oop import StateHA

# Create a state for humid air at 25°C, 1 atm, 60% RH
state = StateHA('T', 298.15, 'P', 101325, 'R', 0.6)

# Access properties using property codes
humidity_ratio = state.get('W')
wet_bulb = state.get('B') - 273.15  # Convert to Celsius
enthalpy = state.get('H')

# Get multiple properties in one call
temp, pressure, rel_humidity = state.get('T', 'P', 'R')

# View current constraint values
constraints = state.constraints()
print(constraints)  # {'T': 298.15, 'P': 101325, 'R': 0.6}

# Update a constraint
state.reset('T', 303.15)  # Change temperature to 30°C

# Replace a constraint with a different property
state.replace('R', 'W', 0.015)  # Replace RH with humidity ratio
```

### Pure Fluid Properties

```python
from coolprop_oop import StateProps

# Create a state for water at 100°C, 1 atm
water = StateProps('T', 373.15, 'P', 101325, 'water')

# Access properties using property codes
density = water.get('D')
enthalpy = water.get('H')
entropy = water.get('S')

# Get multiple properties in one call
temp, pressure = water.get('T', 'P')

# View current constraint values
constraints = water.constraints()
print(constraints)  # {'T': 373.15, 'P': 101325, 'fluid': 'water'}

# Update a constraint
water.reset('T', 393.15)  # Change temperature to 120°C

# Replace a constraint with a different property
water.replace('P', 'D', 900.0)  # Replace pressure with density
```

### Property Codes (CoolProp 6.7.0)

#### Humid Air Properties (`StateHA`)
- `'T'`: Dry Bulb Temperature [K]
- `'B'`: Wet bulb temperature [K]
- `'D'`: Dew point temperature [K]
- `'P'`: Pressure [Pa]
- `'V'`: Mixture volume [m³/kg dry air]
- `'R'`: Relative humidity [0-1]
- `'W'`: Humidity ratio [kg water/kg dry air]
- `'H'`: Mixture enthalpy [J/kg dry air]
- `'S'`: Mixture entropy [J/kg dry air/K]
- `'C'`: Mixture specific heat [J/kg dry air/K]
- `'M'`: Mixture viscosity [Pa-s]
- `'K'`: Mixture thermal conductivity [W/m/K]

#### Pure Fluid Properties (`StateProps`)
- `'T'`: Temperature [K]
- `'P'`: Pressure [Pa]
- `'D'`: Density [kg/m³]
- `'H'`: Specific enthalpy [J/kg]
- `'S'`: Specific entropy [J/kg-K]
- `'Q'`: Vapor quality [-]
- `'C'`: Specific heat capacity at constant pressure [J/kg-K]
- `'O'`: Specific heat capacity at constant volume [J/kg-K]
- `'U'`: Specific internal energy [J/kg]

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