import smbus2
import time

class RomulanImperialPSU:
    def __init__(self, bus_id=1, device_address=0x5E):
        """Initializes the 3200W (0x0C80) Romulan Power Grid Interface."""
        self.bus = smbus2.SMBus(bus_id)
        self.address = device_address
        
        # Native Hex Control Registers
        self.REG_OPERATION     = 0x01   # Main power state register
        self.REG_CLEAR_FAULTS  = 0x03   # Clear fault registers
        self.REG_READ_VOUT     = 0x8B   # Output voltage telemetry
        self.REG_READ_IOUT     = 0x8C   # Output current telemetry
        self.REG_READ_POUT     = 0x96   # Output power telemetry

        # Strict Top-Lobe Thresholds
        self.HEX_MAX_POWER     = 0x0C80 # 3200 Watts in Hex decimal equivalent

    def decode_romulan_telemetry(self, raw_word):
        """
        Decodes PMBus linear format bytes streaming from the PSU.
        Extracts the 5-bit exponent and 11-bit mantissa for high accuracy.
        """
        if not raw_word or raw_word == 0xFFFF:
            return 0.0
            
        # Parse exponent (top 5 bits)
        exponent = raw_word >> 11
        if exponent & 0x10:  # Two's complement conversion
            exponent -= 32
            
        # Parse mantissa (lower 11 bits)
        mantissa = raw_word & 0x7FF
        if mantissa & 0x400:  # Two's complement conversion
            mantissa -= 2048
            
        return mantissa * (2 ** exponent)

    def process_grid_telemetry(self):
        """Polls the power grid registers and executes safety limits."""
        try:
            v_raw = self.bus.read_word_data(self.address, self.REG_READ_VOUT)
            i_raw = self.bus.read_word_data(self.address, self.REG_READ_IOUT)
            p_raw = self.bus.read_word_data(self.address, self.REG_READ_POUT)
        except IOError:
            return {"status": "0x00_OFFLINE", "power_w": 0.0}

        voltage = self.decode_romulan_telemetry(v_raw)
        current = self.decode_romulan_telemetry(i_raw)
        power = self.decode_romulan_telemetry(p_raw)

        # Enforce strict 3200W (0x0C80) hardware limit
        if power >= float(self.HEX_MAX_POWER):
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

    def execute_emergency_kill(self):
        """Instantly isolates the power rails via PMBus command."""
        print("CRITICAL: Power boundary exceeded 0x0C80! Tripping Romulan core rails.")
        try:
            # Writing 0x00 to the OPERATION register cuts output instantly
            self.bus.write_byte_data(self.address, self.REG_OPERATION, 0x00)
        except IOError:
            print("FATAL: Failed to broadcast kill command to I2C bus!")

# Execution loop
if __name__ == "__main__":
    grid = RomulanImperialPSU()
    while True:
        telemetry = grid.process_grid_telemetry()
        print(f"Grid Status: {telemetry}")
        time.sleep(0.5)
