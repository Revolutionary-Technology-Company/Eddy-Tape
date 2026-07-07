import math
import json

class RomulanRoutePlotter:
    def __init__(self, max_incline=30.0, max_turn_increment=45.0):
        """Initializes the spatial route parser and flight-path compiler."""
        self.MAX_INCLINE = max_incline
        self.MAX_TURN_INCREMENT = max_turn_increment

    def parse_3d_coordinates(self, point_a, point_b, point_c=None):
        """
        Calculates segment length, incline shifts, and directional turning changes
        between sequential 3D space vectors.
        """
        # Delta vector calculations (A to B)
        dx1 = point_b[0] - point_a[0]
        dy1 = point_b[1] - point_a[1]
        dz1 = point_b[2] - point_a[2]
        
        # Calculate true linear distance across the 3D plane
        segment_length = math.sqrt(dx1**2 + dy1**2 + dz1**2)
        horizontal_dist = math.sqrt(dx1**2 + dy1**2)
        
        # Calculate pitch vector (incline)
        pitch_rad = math.atan2(dz1, horizontal_dist) if horizontal_dist != 0 else 0
        pitch_deg = math.degrees(pitch_rad)
        
        # Calculate yaw vector (turn increment) if three coordinates are provided
        yaw_change_deg = 0.0
        if point_c is not None:
            dx2 = point_c[0] - point_b[0]
            dy2 = point_c[1] - point_b[1]
            
            heading_1 = math.atan2(dy1, dx1)
            heading_2 = math.atan2(dy2, dx2)
            
            yaw_change_rad = heading_2 - heading_1
            # Normalize angle to -pi to +pi bounds
            yaw_change_rad = (yaw_change_rad + math.pi) % (2 * math.pi) - math.pi
            yaw_change_deg = abs(math.degrees(yaw_change_rad))

        return segment_length, pitch_deg, yaw_change_deg

    def compile_tape_manifest(self, raw_3d_route):
        """
        Compiles an array of 3D points into actionable instructions for the
        tape-laying robot, enforcing physical safety overrides.
        """
        print(f"Analyzing raw trajectory data array ({len(raw_3d_route)} node points)...")
        tape_manifest = []
        
        for i in range(len(raw_3d_route) - 1):
            pt_a = raw_3d_route[i]
            pt_b = raw_3d_route[i+1]
            pt_c = raw_3d_route[i+2] if (i + 2) < len(raw_3d_route) else None
            
            length, incline, turn = self.parse_3d_coordinates(pt_a, pt_b, pt_c)
            
            # Enforce structural checks on the physical building limitations
            safety_status = "0x01_PASSED"
            actions = ["CUT_STANDARD_SEGMENT"]
            
            if abs(incline) > self.MAX_INCLINE:
                safety_status = "0xFF_INCLINE_EXCEEDED_HALT"
                actions.append("EMERGENCY_REPLAN_ANGLE")
                
            if turn > self.MAX_TURN_INCREMENT:
                safety_status = "0xFE_TURN_TOO_SHARP"
                actions.append("SPLIT_INTO_GRADUAL_AIRCRAFT_TURNS")
            
            segment_data = {
                "segment_index": i,
                "cut_length_mm": round(length * 1000.0, 1), # Scaled to mm for KiCad manufacturing
                "incline_degrees": round(incline, 2),
                "next_turn_degrees": round(turn, 2),
                "hex_safety_code": safety_status,
                "robot_execution_directives": actions
            }
            tape_manifest.append(segment_data)
            
        return tape_manifest

# --- Deployment / Run Test Suite ---
if __name__ == "__main__":
    plotter = RomulanRoutePlotter()
    
    # Example 3D Route Array: [X, Y, Z] coordinates in meters
    # Simulates entering a building, scaling a ramp, and taking a structured gradual turn
    industrial_3d_route = [
        [0.0, 0.0, 0.0],    # Node 0: Entry Point
        [5.0, 0.0, 0.0],    # Node 1: Straight tracking run
        [8.0, 0.0, 1.73],   # Node 2: Climbing a 30-degree ramp board structure
        [11.0, 3.0, 1.73],  # Node 3: Sharp vector turn check
        [11.0, 8.0, 1.73]   # Node 4: Exiting straight path
    ]
    
    compiled_tape_output = plotter.compile_tape_manifest(industrial_3d_route)
    
    # Output the structured configuration profiles for the tape robot
    print("\n=== Actionable Tape Slicing & Route Manifest ===")
    print(json.dumps(compiled_tape_output, indent=2))
