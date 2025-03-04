from CoolProp.CoolProp import HAPropsSI, PropsSI

class StateHA:
    """
    A class representing the thermodynamic state of humid air.
    
    This class provides an object-oriented interface to CoolProp's HAPropsSI function
    for humid air properties. It automatically calculates and caches common properties
    for easy access.
    
    Property codes used in this class are compatible with CoolProp version 6.7.0.
    
    Property Codes:
        'T': Dry Bulb Temperature [K]
        'B': Wet bulb temperature [K]
        'D': Dew point temperature [K]
        'P': Pressure [Pa]
        'V': Mixture volume [m³/kg dry air]
        'R': Relative humidity [0-1]
        'W': Humidity ratio [kg water/kg dry air]
        'H': Mixture enthalpy [J/kg dry air]
        'S': Mixture entropy [J/kg dry air/K]
        'C': Mixture specific heat [J/kg dry air/K]
        'M': Mixture viscosity [Pa-s]
        'K': Mixture thermal conductivity [W/m/K]
        
    Properties are accessed using the get() method rather than direct attributes.
    
    Example:
        >>> # Create state at 25°C, 1 atm, 60% RH
        >>> state = StateHA('P', 101325, 'T', 298.15, 'R', 0.6)
        >>> print(f"Humidity ratio: {state.get('W'):.4f} kg/kg")
        Humidity ratio: 0.0120 kg/kg
        >>> print(f"Dew point: {state.get('D')-273.15:.1f}°C")
        Dew point: 16.7°C
    """

    def __init__(self, *args):
        """
        Initialize a StateHA object for humid air properties.
        
        Args:
            *args: Six arguments in the order: prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value
                  where prop_name is a CoolProp property code (str) and value is a float.
                  This format follows the HAPropsSI's parameter order.
        
        Example:
            >>> # Create state at 25°C, 1 atm, 60% RH
            >>> state = StateHA('P', 101325, 'T', 298.15, 'R', 0.6)
        """
        self._constraints = {}
        
        if args:
            if len(args) != 6:
                raise ValueError("StateHA requires exactly 6 arguments: prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value")
            
            # Check that odd-indexed arguments are strings (property codes)
            if not all(isinstance(args[i], str) for i in range(0, 6, 2)):
                raise ValueError("Property names must be strings")
            
            # Check that even-indexed arguments are numeric (property values)
            if not all(isinstance(args[i], (int, float)) for i in range(1, 6, 2)):
                raise ValueError("Property values must be numeric")
            
            # Store constraints
            self._constraints[args[0]] = args[1]
            self._constraints[args[2]] = args[3]
            self._constraints[args[4]] = args[5]
    
    def replace(self, old_prop, new_prop, value):
        """
        Replace one constraint with a new constraint.
        
        This method updates the state by replacing one constraint with a new one.
        
        Args:
            old_prop (str): The property code to remove from constraints
            new_prop (str): The property code to add as a constraint
            value (float): The value for the new property constraint
        
        Returns:
            StateHA: The current object for method chaining.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> state.replace('R', 'W', 0.01)  # Replace RH with humidity ratio
        """
        if old_prop not in self._constraints:
            raise ValueError(f"Property '{old_prop}' is not a current constraint")
        
        if not isinstance(new_prop, str):
            raise ValueError("New property name must be a string")
            
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Remove old constraint and add new one
        del self._constraints[old_prop]
        self._constraints[new_prop] = value
        
        return self
    
    def reset(self, prop, value):
        """
        Reset a single property constraint to a new value.
        
        This method updates an existing property constraint with a new value.
        
        Args:
            prop (str): The property code to reset
            value (float): The new value for the property constraint
        
        Returns:
            StateHA: The current object for method chaining.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> state.reset('T', 303.15)  # Update temperature to 30°C
        """
        if prop not in self._constraints:
            raise ValueError(f"Property '{prop}' is not a current constraint")
        
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Update the constraint value
        self._constraints[prop] = value
        
        return self
    
    def get(self, *props):
        """
        Get specific properties from the current state.
        
        Args:
            *props: One or more property codes to retrieve.
                Valid options include (compatible with CoolProp 6.7.0):
                'T': Dry Bulb Temperature [K]
                'B': Wet bulb temperature [K]
                'D': Dew point temperature [K]
                'P': Pressure [Pa]
                'V': Mixture volume [m³/kg dry air]
                'R': Relative humidity [0-1]
                'W': Humidity ratio [kg water/kg dry air]
                'H': Mixture enthalpy [J/kg dry air]
                'S': Mixture entropy [J/kg dry air/K]
                'C': Mixture specific heat [J/kg dry air/K]
                'M': Mixture viscosity [Pa-s]
                'K': Mixture thermal conductivity [W/m/K]
            
        Returns:
            float or list: The value(s) of the requested properties. If a single property 
                  is requested, returns a float; otherwise, returns a list of floats.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> h = state.get('H')  # Get specific enthalpy
            >>> h, s = state.get('H', 'S')  # Get enthalpy and entropy
        """
        if not props:
            raise ValueError("At least one property must be specified")
        
        if len(self._constraints) != 3:
            raise ValueError("State is not fully defined. Need exactly 3 constraints.")
        
        # Extract constraints for HAPropsSI call
        props_list = []
        for k, v in self._constraints.items():
            props_list.extend([k, v])
        
        # Calculate requested properties
        result = []
        for prop in props:
            value = HAPropsSI(prop, *props_list)
            result.append(value)
        
        # Return single value if only one property requested
        if len(props) == 1:
            return result[0]
        
        return result

    def constraints(self):
        """
        Returns the current set of properties constraining the state with their values.
        
        Returns:
            dict: A dictionary of property names and their values that are currently set as constraints.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> state.constraints()
            {'T': 293.15, 'P': 101325, 'R': 0.5}
        """
        return self._constraints.copy()

class StateProps:
    """
    A class representing the thermodynamic state of a pure fluid.
    
    This class provides an object-oriented interface to CoolProp's PropsSI function
    for pure fluid properties. It automatically calculates and caches common properties
    for easy access.
    
    Property codes used in this class are compatible with CoolProp version 6.7.0.
    
    Property Codes:
        'T': Temperature [K]
        'P': Pressure [Pa]
        'D': Density [kg/m³]
        'H': Specific enthalpy [J/kg]
        'S': Specific entropy [J/kg-K]
        'U': Specific internal energy [J/kg]
        'Q': Vapor quality [-]
        'C': Specific heat capacity at constant pressure [J/kg-K]
        'O': Specific heat capacity at constant volume [J/kg-K]
    
    Properties are accessed using the get() method rather than direct attributes.
    
    Example:
        >>> # Create state for water at 100°C, 1 atm
        >>> water = StateProps('P', 101325, 'T', 373.15, 'water')
        >>> print(f"Density: {water.get('D'):.1f} kg/m³")
        Density: 0.6 kg/m³
        >>> # Get information about available properties
    """
    
    def __init__(self, *args):
        """
        Initialize a StateProps object for pure fluid properties.
        
        Args:
            *args: Five arguments in the order: prop1_name, prop1_value, prop2_name, prop2_value, fluid_name
                  where prop_name is a CoolProp property code (str), value is a float, and fluid_name is a string.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
        """
        self._constraints = {}
        self._fluid = None
        
        if args:
            if len(args) != 5:
                raise ValueError("StateProps requires exactly 5 arguments: prop1_name, prop1_value, prop2_name, prop2_value, fluid_name")
            
            # Check that property names are strings
            if not isinstance(args[0], str) or not isinstance(args[2], str):
                raise ValueError("Property names must be strings")
            
            # Check that property values are numeric
            if not isinstance(args[1], (int, float)) or not isinstance(args[3], (int, float)):
                raise ValueError("Property values must be numeric")
            
            # Check that fluid name is a string
            if not isinstance(args[4], str):
                raise ValueError("Fluid name must be a string")
            
            # Store constraints and fluid
            self._constraints[args[0]] = args[1]
            self._constraints[args[2]] = args[3]
            self._fluid = args[4]

    def replace(self, old_prop, new_prop, value):
        """
        Replace one constraint with a new constraint.
        
        This method updates the state by replacing one constraint with a new one.
        
        Args:
            old_prop (str): The property code to remove from constraints
            new_prop (str): The property code to add as a constraint
            value (float): The value for the new property constraint
        
        Returns:
            StateProps: The current object for method chaining.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> state.replace('P', 'D', 958.4)  # Replace pressure with density
        """
        if old_prop not in self._constraints:
            raise ValueError(f"Property '{old_prop}' is not a current constraint")
        
        if not isinstance(new_prop, str):
            raise ValueError("New property name must be a string")
            
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Remove old constraint and add new one
        del self._constraints[old_prop]
        self._constraints[new_prop] = value
        
        return self
    
    def reset(self, prop, value):
        """
        Reset a single property constraint to a new value.
        
        This method updates an existing property constraint with a new value,
        without changing the fluid type.
        
        Args:
            prop (str): The property code to reset
            value (float): The new value for the property constraint
        
        Returns:
            StateProps: The current object for method chaining.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> state.reset('T', 393.15)  # Update temperature to 120°C
        """
        if prop not in self._constraints:
            raise ValueError(f"Property '{prop}' is not a current constraint")
        
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Update the constraint value
        self._constraints[prop] = value
        
        return self
    
    def get(self, *props):
        """
        Get specific properties from the current state.
        
        Args:
            *props: One or more property codes to retrieve.
                Valid options include (compatible with CoolProp 6.7.0):
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'D': Density [kg/m³]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'Q': Vapor quality [-]
                - 'C': Specific heat capacity at constant pressure [J/kg-K]
                - 'O': Specific heat capacity at constant volume [J/kg-K]
            
        Returns:
            float or list: The value(s) of the requested properties. If a single property 
                  is requested, returns a float; otherwise, returns a list of floats.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> h = state.get('H')  # Get specific enthalpy
            >>> h, s = state.get('H', 'S')  # Get enthalpy and entropy
        """
        if not props:
            raise ValueError("At least one property must be specified")
        
        if len(self._constraints) != 2:
            raise ValueError("State is not fully defined. Need exactly 2 constraints.")
        
        if not self._fluid:
            raise ValueError("Fluid not specified")
        
        # Extract constraints for PropsSI call
        input_props = []
        input_vals = []
        for k, v in self._constraints.items():
            input_props.append(k)
            input_vals.append(v)
        
        # Calculate requested properties
        result = []
        for prop in props:
            value = PropsSI(prop, input_props[0], input_vals[0], input_props[1], input_vals[1], self._fluid)
            result.append(value)
        
        # Return single value if only one property requested
        if len(props) == 1:
            return result[0]
        
        return result
    
    def constraints(self):
        """
        Returns the current set of properties constraining the state with their values.
        
        Returns:
            dict: A dictionary of property names and their values that are currently 
                 set as constraints, including the fluid name.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> state.constraints()
            {'T': 373.15, 'P': 101325, 'fluid': 'water'}
        """
        constraints = self._constraints.copy()
        if self._fluid:
            constraints['fluid'] = self._fluid
        return constraints