from CoolProp.CoolProp import HAPropsSI, PropsSI
import warnings

def state_setter_HA(func):
    """
    Decorator for property setters that manages state constraints for humid air properties.
    
    Checks the number of constraints and version before allowing property to be set.
    Prevents overconstraining the system while allowing property updates when version changes.
    Also tracks which properties have been set for state validation.
    """
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        
        # Initialize constraints set if not exists
        if not hasattr(self, '_constraints_set'):
            self._constraints_set = set()
        
        # Allow setting if we have 0 or 1 constraint
        if len(self._constraints_set) < 2:
            func(self, value)
            self._constraints_set.add(prop_name)
            return
            
        # If we have 2 constraints, test validity before adding third
        if len(self._constraints_set) == 2:
            try:
                self.test_state_validity(self._constraints_set, prop_name, value)
                func(self, value)
                self._constraints_set.add(prop_name)
            except ValueError as e:
                raise ValueError(f"Cannot set {prop_name} - {str(e)}")
            return
            
        # If we have 3 constraints, only allow if property was previously set
        if len(self._constraints_set) == 3:
            if prop_name not in self._constraints_set:
                raise ValueError(f"Cannot set {prop_name} - system is already fully constrained.")
            other_props = self._constraints_set - {prop_name}
            try:
                self.test_state_validity(other_props, prop_name, value)
                func(self, value)
            except ValueError as e:
                raise ValueError(f"Cannot set {prop_name} - {str(e)}")
            return
            
    return wrapper

def unsettable_property(func):
    """
    Decorator for properties that should not be settable.
    
    Raises an AttributeError if an attempt is made to set the property.
    Used for properties that are calculated from other state variables and
    should not be directly set.
    """
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        raise AttributeError(f"{prop_name} cannot be set directly as it is calculated "
                           "from other state properties.")
    return wrapper

def cached_property(func):
    """
    Decorator for property getters that implements version-based caching.
    
    If the property is part of the constraints set, returns the directly set value.
    Otherwise, checks if the cached value is from the current state version before returning it.
    If not current, recalculates the property and updates the cache.
    """
    def getter(self):
        prop_name = func.__name__
        version_attr = f"_{prop_name}_version"
        value_attr = f"_{prop_name}"
        
        # If we don't have 3 constraints yet, can't calculate anything
        if not hasattr(self, '_constraints_set') or len(self._constraints_set) < 3:
            return getattr(self, value_attr)
        
        # If this property is one of our constraints, return the set value
        if prop_name in self._constraints_set:
            return getattr(self, value_attr)
        
        # Otherwise, check if we need to update the cached value
        if (not hasattr(self, version_attr) or 
            getattr(self, version_attr) != self._version):
            # Get the CoolProp property name from our mapping
            coolprop_name = self._prop_map[prop_name]
            # Calculate and store the new value
            value = self.get_prop(coolprop_name)
            setattr(self, value_attr, value)
            # Update the version
            setattr(self, version_attr, self._version)
        
        return getattr(self, value_attr)
    
    return getter

class StateHA:
    """
    A class representing the thermodynamic state of humid air.
    
    This class provides an object-oriented interface to CoolProp's HAPropsSI function
    for humid air properties. It automatically calculates and caches common properties
    for easy access.
    
    Attributes:
        tempk (float): Temperature in Kelvin
        tempc (float): Temperature in Celsius
        press (float): Pressure in Pa
        humrat (float): Humidity ratio in kg/kg
        wetbulb (float): Wet bulb temperature in K
        relhum (float): Relative humidity (0-1)
        vol (float): Specific volume in m³/kg
        enthalpy (float): Specific enthalpy in J/kg
        entropy (float): Specific entropy in J/kg-K
        dewpoint (float): Dew point temperature in K
        density (float): Density in kg/m³
        cp (float): Specific heat capacity at constant pressure in J/kg-K
    
    Example:
        >>> # Create state at 25°C, 1 atm, 60% RH
        >>> state = StateHA(['P', 101325, 'T', 298.15, 'R', 0.6])
        >>> print(f"Humidity ratio: {state.humrat:.4f} kg/kg")
        Humidity ratio: 0.0120 kg/kg
        >>> print(f"Dew point: {state.dewpoint-273.15:.1f}°C")
        Dew point: 16.7°C
    """
    
    _prop_map = {
        'tempk': 'T',
        'tempc': 'T',  # Will need special handling for Celsius conversion
        'press': 'P',
        'humrat': 'W',
        'wetbulb': 'B',
        'relhum': 'R',
        'dewpoint': 'D',
        'vol': 'V',
        'enthalpy': 'H', 
        'entropy': 'S',
        'density': 'D',
        'cp': 'C',
        'viscosity': 'M',
        'conductivity': 'K',
        'compressibility': 'Z',
        'prandtl': 'L'
    }

    def __init__(self, props=None):
        """
        Initialize a StateHA object for humid air properties.
        
        Note:
            While passing props at initialization is still supported for backwards compatibility,
            it is recommended to set properties individually for better performance:
                state = StateHA()
                state.tempk = 293.15
                state.press = 101325
                state.relhum = 0.5
        
        Args:
            props (list, optional): DEPRECATED. Property inputs for HAPropsSI.
                While still supported, direct property setting is preferred.
                [prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value]
        """
        self._tempk = None
        self._tempc = None
        self._press = None
        self._humrat = None
        self._wetbulb = None
        self._relhum = None
        self._vol = None
        self._enthalpy = None
        self._entropy = None
        self._dewpoint = None
        self._density = None
        self._cp = None
        
        self._constraints_set = set()
        
        if props is not None:
            warnings.warn(
                "Initializing with props is deprecated and will be removed in version 2.0.0. "
                "Use direct property setting instead:\n"
                "    state = StateHA()\n"
                "    state.tempk = value\n"
                "    state.press = value\n"
                "    state.relhum = value",
                DeprecationWarning,
                stacklevel=2
            )
            self.set(props)

    @property
    def tempk(self):
        if 'tempk' in self._constraints_set:
            return self._tempk
        if len(self._constraints_set) == 3:
            return self.get_prop('T')
        return self._tempk

    @tempk.setter
    @state_setter_HA
    def tempk(self, value):
        self._tempk = value

    @property
    def tempc(self):
        if 'tempc' in self._constraints_set:
            return self._tempc
        if 'tempk' in self._constraints_set:
            return self._tempk - 273.15
        return self.tempk - 273.15

    @tempc.setter
    @state_setter_HA
    def tempc(self, value):
        self._tempc = value
        self._tempk = value + 273.15

    @property
    def press(self):
        if 'press' in self._constraints_set:
            return self._press
        if len(self._constraints_set) == 3:
            return self.get_prop('P')
        return self._press

    @press.setter
    @state_setter_HA
    def press(self, value):
        self._press = value

    @property
    def relhum(self):
        if 'relhum' in self._constraints_set:
            return self._relhum
        if len(self._constraints_set) == 3:
            return self.get_prop('R')
        return self._relhum

    @relhum.setter
    @state_setter_HA
    def relhum(self, value):
        self._relhum = value

    @property
    def humrat(self):
        if 'humrat' in self._constraints_set:
            return self._humrat
        if len(self._constraints_set) == 3:
            return self.get_prop('W')
        return self._humrat

    @humrat.setter
    @state_setter_HA
    def humrat(self, value):
        self._humrat = value

    @property
    def wetbulb(self):
        if 'wetbulb' in self._constraints_set:
            return self._wetbulb
        if len(self._constraints_set) == 3:
            return self.get_prop('B')
        return self._wetbulb

    @wetbulb.setter
    @state_setter_HA
    def wetbulb(self, value):
        self._wetbulb = value

    @property
    def dewpoint(self):
        return self._dewpoint

    @dewpoint.setter
    @state_setter_HA
    def dewpoint(self, value):
        self._dewpoint = value

    @property
    def vol(self):
        if len(self._constraints_set) == 3:
            return self.get_prop('V')
        return None

    @vol.setter
    def vol(self, value):
        raise AttributeError("vol cannot be set directly")

    @property
    def enthalpy(self):
        if len(self._constraints_set) == 3:
            return self.get_prop('H')
        return None

    @enthalpy.setter
    def enthalpy(self, value):
        raise AttributeError("enthalpy cannot be set directly")

    @property
    def entropy(self):
        if len(self._constraints_set) == 3:
            return self.get_prop('S')
        return None

    @entropy.setter
    def entropy(self, value):
        raise AttributeError("entropy cannot be set directly")

    @property
    def density(self):
        if len(self._constraints_set) == 3:
            vol = self.get_prop('V')
            return 1/vol if vol is not None else None
        return None

    @density.setter
    def density(self, value):
        raise AttributeError("density cannot be set directly")

    @property
    def cp(self):
        if len(self._constraints_set) == 3:
            return self.get_prop('C')
        return None

    @cp.setter
    def cp(self, value):
        raise AttributeError("cp cannot be set directly")

    def set(self, props):
        """
        DEPRECATED: Direct property setting is now preferred over the set method.
        
        Set the properties of the StateHA object using the provided inputs.
        This method will be removed in version 2.0.0.
        
        Instead of:
            state.set(['T', 293.15, 'P', 101325, 'R', 0.5])
        Use:
            state.tempk = 293.15
            state.press = 101325
            state.relhum = 0.5
        
        Args:
            props (list): Property inputs for HAPropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value]
        
        Returns:
            StateHA: The current object for method chaining.
        """
        warnings.warn(
            "The set() method is deprecated and will be removed in version 2.0.0. "
            "Use direct property setting instead (e.g., state.tempk = value).",
            DeprecationWarning,
            stacklevel=2
        )
        
        self.props = props
        # Map CoolProp properties to our setter methods
        prop_map = {
            'T': 'tempk',
            'P': 'press',
            'W': 'humrat',
            'R': 'relhum',
            'B': 'wetbulb',
            'D': 'dewpoint'
        }
        
        # Set properties using our property setters
        for i in range(0, len(props), 2):
            prop_name = props[i]
            value = props[i + 1]
            if prop_name in prop_map:
                setattr(self, prop_map[prop_name], value)
        
        return self
    
    def get_prop(self, prop):
        """
        Get a specific property using HAPropsSI.
        
        Args:
            prop (str): The property to retrieve. Valid options include:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'W': Humidity ratio [kg/kg]
                - 'R': Relative humidity [-]
                - 'B': Wet bulb temperature [K]
                - 'D': Dew point temperature [K]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'V': Specific volume [m³/kg]
                - 'C': Specific heat capacity [J/kg-K]
            
        Returns:
            float: The value of the requested property.
        
        Raises:
            ValueError: If the state is not fully defined (needs 3 constraints)
        """
        if len(self._constraints_set) < 3:
            raise ValueError("Cannot calculate properties until state is fully defined with 3 constraints")
        
        # Build props list from constraints set
        props = []
        for constraint in self._constraints_set:
            coolprop_name = self._prop_map[constraint]
            value = getattr(self, f"_{constraint}")
            # Handle Celsius conversion
            if constraint == 'tempc':
                value = value + 273.15
            props.extend([coolprop_name, value])
        
        return HAPropsSI(prop, *props)

    def test_state_validity(self, current_props, new_prop, new_value):
        """
        Test if the current state properties are physically valid using HAPropsSI.
        
        Args:
            current_props (set): Set of currently set property names
            new_prop (str): Name of the new property being set
            new_value (float): Value of the new property
        
        Returns:
            bool: True if the state is valid, False otherwise.
        
        Raises:
            ValueError: If the combination of properties would create an invalid state,
                      with the specific error message from CoolProp.
        """
        try:
            # Build a test props list with current properties and new value
            test_props = []
            for prop in current_props:
                coolprop_name = self._prop_map[prop]
                value = getattr(self, f"_{prop}")
                # Handle Celsius conversion
                if prop == 'tempc':
                    value = value + 273.15
                test_props.extend([coolprop_name, value])
            
            # Add the new property
            coolprop_new_prop = self._prop_map[new_prop]
            new_value_converted = new_value + 273.15 if new_prop == 'tempc' else new_value
            test_props.extend([coolprop_new_prop, new_value_converted])
            
            # Try to calculate one of the input properties to validate state
            input_prop = self._prop_map[list(current_props)[0]]  # Use first property from current set
            HAPropsSI(input_prop, *test_props)
            return True
            
        except ValueError as e:
            # Re-raise with the CoolProp error message for better explanation
            raise ValueError(f"Invalid state: {str(e)}") from None

class StatePROPS:
    """
    A class representing the thermodynamic state of a pure fluid.
    
    This class provides an object-oriented interface to CoolProp's PropsSI function
    for pure fluid properties. It automatically calculates and caches common properties
    for easy access.
    
    Attributes:
        tempk (float): Temperature in Kelvin
        tempc (float): Temperature in Celsius
        press (float): Pressure in Pa
        dens (float): Density in kg/m³
        enthalpy (float): Specific enthalpy in J/kg
        entropy (float): Specific entropy in J/kg-K
        quality (float): Vapor quality (0-1), or None if not in two-phase region
        cp (float): Specific heat capacity at constant pressure in J/kg-K
        cv (float): Specific heat capacity at constant volume in J/kg-K
    
    Example:
        >>> # Create state for water at 100°C, 1 atm
        >>> water = StatePROPS(['P', 101325, 'T', 373.15, 'water'])
        >>> print(f"Density: {water.dens:.1f} kg/m³")
        Density: 0.6 kg/m³
        >>> # Create state for R134a at 25°C, 10 bar
        >>> r134a = StatePROPS(['P', 1e6, 'T', 298.15, 'R134a'])
        >>> print(f"Density: {r134a.dens:.1f} kg/m³")
        Density: 1209.0 kg/m³
    """
    
    def __init__(self, props=None):
        """
        Initialize a StatePROPS object for pure fluid properties.
        
        Args:
            props (list, optional): Property inputs for PropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, fluid_name]
                where prop_name can be:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'D': Density [kg/m³]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'Q': Vapor quality [-]
                If provided, properties are calculated immediately.
        
        Example:
            >>> state = StatePROPS(['T', 373.15, 'P', 101325, 'water'])
        """
        self.props = None
        self.tempk = None
        self.tempc = None
        self.press = None
        self.dens = None
        self.enthalpy = None
        self.entropy = None
        self.quality = None
        self.cp = None
        self.cv = None
        
        if props is not None:
            self.set(props)
    
    def set(self, props):
        """
        Set the properties of the StatePROPS object using the provided inputs.
        
        This method calculates all state properties based on the two input properties
        and fluid name provided. It uses CoolProp's PropsSI function internally.
        
        Args:
            props (list): Property inputs for PropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, fluid_name]
        
        Returns:
            StatePROPS: The current object for method chaining.
        
        Example:
            >>> state = StatePROPS()
            >>> state.set(['T', 373.15, 'P', 101325, 'water'])
            >>> print(f"{state.tempc:.1f}°C")
            100.0°C
        """
        self.props = props
        self.tempk = self.get_prop("T")
        self.tempc = self.tempk - 273.15
        self.press = self.get_prop("P")
        self.dens = self.get_prop("D")
        self.enthalpy = self.get_prop("H")
        self.entropy = self.get_prop("S")
        self.quality = self.get_prop("Q")
        self.cp = self.get_prop("C")
        self.cv = self.get_prop("O")
        
        return self
    
    def get_prop(self, prop):
        """
        Get a specific property using PropsSI.
        
        Args:
            prop (str): The property to retrieve. Valid options include:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'D': Density [kg/m³]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'Q': Vapor quality [-]
                - 'C': Specific heat capacity at constant pressure [J/kg-K]
                - 'O': Specific heat capacity at constant volume [J/kg-K]
            
        Returns:
            float: The value of the requested property.
        
        Example:
            >>> state = StatePROPS(['T', 373.15, 'P', 101325, 'water'])
            >>> h = state.get_prop('H')  # Get specific enthalpy
        """
        return PropsSI(prop, *self.props)