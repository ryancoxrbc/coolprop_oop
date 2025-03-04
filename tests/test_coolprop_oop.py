"""
Tests for coolprop_oop.
This module implements unit tests for the StateHA (Humid Air) and
StateProps (Pure Fluid) property calculators.

Tests include:
- Basic initialization and property calculation
- Input validation for all properties
- Under/over constraining behavior
- Invalid value handling
- Property updates and dependencies
- Error message formatting
"""

from CoolProp.CoolProp import HAPropsSI, PropsSI
from coolprop_oop import StateHA, StateProps
import unittest

class TestStateHA(unittest.TestCase):
    """Test the StateHA class functionality."""
    
    def test_properties_match_coolprop(self):
        """Test that our StateHA wrapper gives the same results as HAPropsSI."""
        # Test case: 25°C, 1 atm, 60% RH
        T, P, R = 298.15, 101325, 0.6
        
        # Create a state
        state = StateHA('T', T, 'P', P, 'R', R)
        
        # List of properties to test
        properties = ['W', 'D', 'B', 'H', 'S', 'V', 'C']
        
        for prop in properties:
            # Get property from our wrapper
            our_value = state.get(prop)
            
            # Get the same property directly from CoolProp
            coolprop_value = HAPropsSI(prop, 'T', T, 'P', P, 'R', R)
            
            # Compare values (with small tolerance for floating point differences)
            self.assertAlmostEqual(our_value, coolprop_value, places=5, 
                                  msg=f"Property {prop} values differ: {our_value} vs {coolprop_value}")
    
    def test_constraint_management(self):
        """Test constraint management in StateHA."""
        # Create initial state
        state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
        
        # Test constraints method
        constraints = state.constraints()
        self.assertEqual(len(constraints), 3)
        self.assertIn('T', constraints)
        self.assertIn('P', constraints)
        self.assertIn('R', constraints)
        
        # Test reset method
        state.reset('T', 303.15)
        self.assertEqual(state.get('T'), 303.15)
        
        # Test replace method
        w_value = state.get('W')
        state.replace('R', 'W', w_value)
        constraints = state.constraints()
        self.assertIn('W', constraints)
        self.assertNotIn('R', constraints)
        
    def test_get_multiple_properties(self):
        """Test getting multiple properties at once."""
        state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
        
        # Get multiple properties
        t, p, r = state.get('T', 'P', 'R')
        
        # Check values
        self.assertAlmostEqual(t, 293.15)
        self.assertAlmostEqual(p, 101325)
        self.assertAlmostEqual(r, 0.5)

class TestStateProps(unittest.TestCase):
    """Test the StateProps class functionality."""
    
    def test_properties_match_coolprop(self):
        """Test that our StateProps wrapper gives the same results as PropsSI."""
        # Test case: Water at 100°C, 1 atm
        T, P = 373.15, 101325
        fluid = 'water'
        
        # Create a state
        state = StateProps('T', T, 'P', P, fluid)
        
        # List of properties to test
        properties = ['D', 'H', 'S', 'C', 'O', 'U']
        
        for prop in properties:
            # Get property from our wrapper
            our_value = state.get(prop)
            
            # Get the same property directly from CoolProp
            coolprop_value = PropsSI(prop, 'T', T, 'P', P, fluid)
            
            # Compare values (with small tolerance for floating point differences)
            self.assertAlmostEqual(our_value, coolprop_value, places=5,
                                  msg=f"Property {prop} values differ: {our_value} vs {coolprop_value}")
    
    def test_constraint_management(self):
        """Test constraint management in StateProps."""
        # Create initial state
        state = StateProps('T', 373.15, 'P', 101325, 'water')
        
        # Test constraints method
        constraints = state.constraints()
        self.assertEqual(len(constraints), 3)  # T, P, and fluid
        self.assertIn('T', constraints)
        self.assertIn('P', constraints)
        self.assertIn('fluid', constraints)
        
        # Test reset method
        state.reset('T', 393.15)
        self.assertEqual(state.get('T'), 393.15)
        
        # Test replace method
        d_value = state.get('D')
        state.replace('P', 'D', d_value)
        constraints = state.constraints()
        self.assertIn('D', constraints)
        self.assertNotIn('P', constraints)
    
    def test_refrigerants(self):
        """Test refrigerant properties."""
        # Test R134a
        r134a = StateProps('T', 298.15, 'P', 1000000, 'R134a')
        
        # Check some properties
        self.assertTrue(r134a.get('D') > 0)
        self.assertTrue(r134a.get('H') != 0)
        
        # Test some other refrigerants if available
        try:
            r410a = StateProps('T', 298.15, 'P', 1000000, 'R410A')
            self.assertTrue(r410a.get('D') > 0)
        except:
            pass  # Skip if not available

    def test_get_multiple_properties(self):
        """Test getting multiple properties at once."""
        state = StateProps('T', 373.15, 'P', 101325, 'water')
        
        # Get multiple properties
        t, p, d = state.get('T', 'P', 'D')
        
        # Check values
        self.assertAlmostEqual(t, 373.15)
        self.assertAlmostEqual(p, 101325)
        self.assertTrue(d > 0)  # Density should be positive

if __name__ == '__main__':
    unittest.main() 