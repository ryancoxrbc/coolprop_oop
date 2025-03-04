# CoolProp-OOP

An object-oriented wrapper for [CoolProp](http://www.coolprop.org/) thermodynamic properties. This library provides an intuitive, Pythonic interface to CoolProp's functionality for both humid air and pure fluid property calculations.

## Features

- **Object-oriented interface** to CoolProp's functionality
- **Property validation** to prevent physically impossible states
- **All thermodynamic properties are directly settable** - enthalpy, entropy, and any other property can be used as a constraint
- **Automatic caching** of calculated properties for better performance
- Support for both **Humid Air** (`StateHA`) and **Pure Fluids** (`StateProps`)
- Comprehensive **state validation** with helpful error messages
- **Fully Pythonic API** with property-based getters and setters

CoolProp-OOP provides an intuitive, object-oriented interface to CoolProp's thermodynamic property calculations for both humid air and pure fluids. It simplifies property access and calculations through two main classes: `StateHA` for humid air properties and `StateProps` for pure fluid properties.

## Installation

```bash
pip install coolprop-oop
```

## Features

- Easy-to-use object-oriented interface
- Simple property constraint management
- Support for both humid air and pure fluid calculations
- Consistent SI unit system
- Compatible with CoolProp 6.7.0

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
- `'T'`: Temperature [K]
- `'P'`: Pressure [Pa]
- `'W'`: Humidity ratio [kg/kg dry air]
- `'R'`: Relative humidity [0-1]
- `'D'`: Dew point temperature [K]
- `'B'`: Wet bulb temperature [K]
- `'V'`: Specific volume [m³/kg dry air]
- `'H'`: Specific enthalpy [J/kg dry air]
- `'S'`: Specific entropy [J/kg dry air/K]
- `'C'`: Specific heat capacity [J/kg dry air/K]

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

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 