#!/usr/bin/env python3
"""
Romulan Imperial Power Supply and Navigation Control System
Filename: hex_native_psu.py
Target Hardware: 3200W (0x0C80) Grid System & Cuttable Parallel Eddy-Tape Layout
Application: High-Stability Hazardous Cargo Transport & Military Industrial Logistics
"""

import math
import time
import smbus2

class RomulanMasterTapeSystem:
    def __init__(self, bus_id=1, device_address=0x5E):
        """
        Initializes the unified power, logistics, and navigation grid.
        Base address 0x5E targets industrial-grade PMBus multi-rail supplies.
        """
        try:
            self.bus = smbus2.SMBus(bus_id)
        except IOError:
            print(f"WARNING: I2C bus {bus_id} unavailable. Running in simulation mode.")
            self.bus = None

        self.address = device_address
        
        # Native PMBus & Custom Hex Control Registers
        self.REG_OPERATION     = 0x01   # Main power output control register
        self.REG_CLEAR_FAULTS  = 0x03   # Clear safety trip faults
        self.REG_POWER_CTRL    = 0x20   # Custom register to output duty cycle to tape segments
        self.REG_READ_VOUT     = 0x8B   # Output voltage telemetry register
        self.REG_READ_IOUT     = 0x8C   # Output current telemetry register
        self.REG_READ_POUT     = 0x96   # Total system wattage telemetry register

        # Rigid Top-Lobe Structural Boundaries
        self.MAX_POWER_HEX     = 0x0C80 # 3200 Watts max cutoff point
        self.MAX_POWER_DEC     = 3200.0

        # Military Asset Manifest Database (MIL-STD-129 / ISO 6346 Compliance)
        self.inventory_manifest = {
            "BARREL_0x0A1": {
                "contents": "Industrial Cobalt-60 Isotopes",
                "hazard_class": "Class_7_Radioactive",
                "un_number": "UN2916",
                "weight_kg": 450.0,
                "dimensions_cm": {"radius": 30, "height": 90},
                "weight_distribution": "BOTTOM_HEAVY", # Low risk footprint
                "tetris_footprint_hex": "0x04"         # Standard square sabot slot
            },
            "BARREL_0x0B2": {
                "contents": "Heavy Metal Sludge",
                "hazard_class": "Class_9_Hazardous",
                "un_number": "UN3082",
                "weight_kg": 600.0,
                "dimensions_cm": {"radius": 35, "height": 95},
                "weight_distribution": "TOP_HEAVY",    # High wobble / spin risk
                "tetris_footprint_hex": "0x06"         # Oversized reinforced sabot slot
            }
        }

    def decode_pmbus_linear(self, raw_word):
        """
        Parses PMBus standard 16-bit linear format streaming from the power unit.
        Extracts 5-bit exponent and 11-bit mantissa to map system telemetry.
        """
        if not raw_word or raw_word == 0xFFFF:
            return 0.0
            
        exponent = raw_word >> 11
        if exponent & 0x10:  # Handle 5-bit two's complement sign bit
            exponent -= 32
            
        mantissa = raw_word & 0x7FF
        if mantissa & 0x400:  # Handle 11-bit two's complement sign bit
            mantissa -= 2048
            
        return float(mantissa * (2 ** exponent))

    def evaluate_grid_safety(self):
        """Polls multi-rail busbar telemetry and enforces the 0x0C80 maximum limit."""
        if not self.bus:
            return {"status_hex": "0x01_SIMULATED_NOMINAL", "power_w": 1200.0}

        try:
            v_raw = self.bus.read_word_data(self.address, self.REG_READ_VOUT)
            i_raw = self.bus.read_word_data(self.address, self.REG_READ_IOUT)
            p_raw = self.bus.read_word_data(self.address, self.REG_READ_POUT)
        except IOError:
            print("CRITICAL: Hardware bus unreadable! Emergency stop protocol required.")
            return {"status_hex": "0x00_BUS_FAULT", "power_w": 0.0}

        voltage = self.decode_pmbus_linear(v_raw)
        current = self.decode_pmbus_linear(i_raw)
        power = self.decode_pmbus_linear(p_raw)

        # 3200W Top-Lobe Isolation Guard
        if power >= self.MAX_POWER_DEC:
            self.execute_emergency_kill()
            status = "0xFF_CRITICAL_OVERLOAD_TRIPPED"
        else:
            status = "0x01_GRID_STABLE"

        return {
            "status_code": status,
            "voltage_v": round(voltage, 2),
            "current_a": round(current, 2),
            "power_w": round(power, 2),
            "hex_power_register": hex(p_raw)
        }

    # Insert this class directly into your hex_native_psu.py file
class PhysicalTrackSwitchboard:
    def __init__(self):
        """Defines the mechanical track routing topology."""
        self.switch_registry = {
            "SWITCH_0x01": {"current_position": "STRAIGHT", "line_a": "MAIN_RAMP", "line_b": "STORAGE_BAY_1"},
            "SWITCH_0x02": {"current_position": "STRAIGHT", "line_a": "STORAGE_BAY_1", "line_b": "TURNTABLE_ENTRY"}
        }

    def toggle_junction(self, switch_id, target_direction, bus_handle=None, address=0x5E):
        """
        Commands the tracking robot or mechanical guide rail to divert paths.
        Sends a hex signal over the I2C bus to trigger physical relays.
        """
        if switch_id not in self.switch_registry:
            print(f"ERROR: Track switch {switch_id} does not exist.")
            return False
            
        if target_direction in ["STRAIGHT", "DIVERTED"]:
            self.switch_registry[switch_id]["current_position"] = target_direction
            active_route = (self.switch_registry[switch_id]["line_a"] 
                            if target_direction == "STRAIGHT" 
                            else self.switch_registry[switch_id]["line_b"])
            
            print(f"Junction {switch_id} toggled to {target_direction}. Active path: -> {active_route}")
            
            # Physical Hardware Execution Layer
            if bus_handle:
                try:
                    # Send signal to change the rail direction (0x01 for straight, 0x02 for diverted)
                    signal_byte = 0x01 if target_direction == "STRAIGHT" else 0x02
                    # Target register 0x25 on your distribution PCB to flip the physical relay
                    bus_handle.write_byte_data(address, 0x25, signal_byte)
                except IOError:
                    print(f"ERROR: Failed to transmit hardware switch command to {switch_id}")
            return True
        return False

    def execute_emergency_kill(self):
        """Instantly isolates the parallel tape power rails to safeguard hazardous cargo."""
        print("ALERT: Boundary breach or overload! Isolating core power rails immediately.")
        if self.bus:
            try:
                # Writing 0x00 to OPERATION drops output voltage to 0V instantly
                self.bus.write_byte_data(self.address, self.REG_OPERATION, 0x00)
            except IOError:
                print("FATAL: Failed to broadcast kill sequence across I2C network!")

    def calculate_ramp_push_force(self, mass_kg, incline_deg, mu_rolling=0.05):
        """Calculates exact Newtonian push force required to scale ramp boards safely."""
        g = 9.81
        rad = math.radians(incline_deg)
        
        gravity_component = mass_kg * g * math.sin(rad)
        friction_component = mu_rolling * mass_kg * g * math.cos(rad)
        
        return gravity_component + friction_component

    def calculate_max_turn_velocity(self, radius_m, mu_static=0.6):
        """Computes the physical grip boundary to stop barrels from sliding or spinning out."""
        g = 9.81
        return math.sqrt(mu_static * g * radius_m)

    def process_route_vector(self, barrel_id, current_incline, next_turn_angle, turn_radius_m=4.0):
        """
        Integrates logistics variables with spatial physics to control tape power outputs.
        Parses dimensions and center-of-gravity profiles to mitigate dynamic wobble.
        """
        # 1. Enforce power grid health verification before managing loads
        telemetry = self.evaluate_grid_safety()
        if "TRIPPED" in telemetry["status_code"] or "FAULT" in telemetry["status_code"]:
            return False

        # 2. Extract asset metrics from military database
        if barrel_id not in self.inventory_manifest:
            print(f"LOGISTICS ERROR: Asset {barrel_id} missing from manifest. Blocking route execution.")
            return False
            
        cargo = self.inventory_manifest[barrel_id]
        mass = cargo["weight_kg"]
        dist = cargo["weight_distribution"]
        
        print(f"\n--- [MIL-STD-129] Routing Asset: {barrel_id} ---")
        print(f"Contents: {cargo['contents']} | Tracking Code: {cargo['un_number']}")
        print(f"Footprint Class: {cargo['tetris_footprint_hex']} | Current Grid Load: {telemetry['power_w']}W")

        # 3. Dynamic Ramp Incline Calculation
        required_force = self.calculate_ramp_push_force(mass, current_incline)
        print(f"Ramp Vector: {current_incline}° Incline | Force Required: {required_force:.1f} Newtons")

        # 4. Gradual Turn Throttling Matrix (Aircraft Banking Simulation)
        if next_turn_angle >= 45:
            max_safe_v = self.calculate_max_turn_velocity(turn_radius_m)
            print(f"Approaching Smooth {next_turn_angle}° Turn (Radius: {turn_radius_m}m). Safe Limit: {max_safe_v:.2f} m/s")
            
            # Adjust velocity variables based on physical cargo configurations
            if dist == "TOP_HEAVY":
                print("CRITICAL CAP: Cargo is top-heavy. Restricting loop to 0x30 crawler duty cycle.")
                target_power_hex = 0x30
            else:
                print("STABILITY CHECK: Base footprint nominal. Engaging 0x50 stabilized cornering power.")
                target_power_hex = 0x50
                
            self.execute_arc_transition(next_turn_angle, step_increment=15, power_state=target_power_hex)
        else:
            # Symmetrical baseline calculation for nominal straight-line propulsion
            # If ascending a steep ramp, scale power up proportionally
            if current_incline > 15:
                target_power_hex = 0xC0  # Extra power register allocation for incline boost
            else:
                target_power_hex = 0xA0  # Standard cruise profile
                
            print(f"Path Vector Nominal. Applying standard track driving register: {hex(target_power_hex)}")
            if self.bus:
                try:
                    self.bus.write_byte_data(self.address, self.REG_POWER_CTRL, target_power_hex)
                except IOError:
                    print("ERROR: Lost track connection during baseline write.")

    def execute_arc_transition(self, total_angle, step_increment, power_state):
        """Sequentially updates segment power registers to safely ease loads through curves."""
        print(f"Executing gradual curve trajectory via {step_increment}° increments...")
        current_heading = 0
        
        while current_heading < total_angle:
            current_heading += step_increment
            if self.bus:
                try:
                    self.bus.write_byte_data(self.address, self.REG_POWER_CTRL, power_state)
                except IOError:
                    print(f"ERROR: Failed to update curve segment at heading: {current_heading}°")
            print(f"  -> Heading: {current_heading}° | Custom Cut-Segment Register: {hex(power_state)}")
            time.sleep(0.3)  # Physical damping interval for momentum stabilization
            
        print("Curvature sequence complete. Transitioning back to vector path baseline.")

# Execution Pipeline Integration
if __name__ == "__main__":
    system = RomulanMasterTapeSystem()
    
    # Run Scenario 1: Stable, bottom-heavy barrel hitting a 30-degree ramp board
system.process_route_vector(barrel_id="BARREL_0x0A1", current_incline=30.0, next_turn_angle=0)

# Run Scenario 2: Dangerous, top-heavy hazardous container navigating a smooth 45-degree corner
system.process_route_vector(barrel_id="BARREL_0x0B2", current_incline=0.0, next_turn_angle=45, turn_radius_m=5.0)
