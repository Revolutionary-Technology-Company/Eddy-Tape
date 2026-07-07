# tape_kicad_gen.py
# Run this inside the KiCad PCB Editor Python Scripting Console
import pcbnew
import math

class RomulanTapeGenerator:
    def __init__(self, segment_count=16, segment_length_mm=100.0):
        self.board = pcbnew.GetBoard()
        self.segments = segment_count
        self.seg_len = segment_length_mm
        
        # Physical Layer Settings
        self.rail_width = pcbnew.FromMM(15.0)     # Heavy 15mm copper rails
        self.node_width = pcbnew.FromMM(2.0)      # 2mm bridge nodes
        self.tape_width = pcbnew.FromMM(50.0)     # Total tape width 50mm
        
        # Layer Mappings
        self.top_layer = pcbnew.F_Cu
        self.bottom_layer = pcbnew.B_Cu

    def generate_parallel_bus(self):
        """Lays down continuous heavy copper rails on the outer edges."""
        total_length = self.segments * self.seg_len
        start_x = pcbnew.FromMM(10.0)
        start_y = pcbnew.FromMM(10.0)
        end_x = start_x + pcbnew.FromMM(total_length)
        
        # Upper Positive Rail (+VCC)
        vcc_y = start_y + (self.rail_width / 2)
        track_vcc = pcbnew.PCB_TRACK(self.board)
        track_vcc.SetStart(pcbnew.VECTOR2I(start_x, vcc_y))
        track_vcc.SetEnd(pcbnew.VECTOR2I(end_x, vcc_y))
        track_vcc.SetWidth(self.rail_width)
        track_vcc.SetLayer(self.top_layer)
        self.board.Add(track_vcc)
        
        # Lower Negative Rail (GND)
        gnd_y = start_y + pcbnew.FromMM(self.tape_width) - (self.rail_width / 2)
        track_gnd = pcbnew.PCB_TRACK(self.board)
        track_gnd.SetStart(pcbnew.VECTOR2I(start_x, gnd_y))
        track_gnd.SetEnd(pcbnew.VECTOR2I(end_x, gnd_y))
        track_gnd.SetWidth(self.rail_width)
        track_gnd.SetLayer(self.top_layer)
        self.board.Add(track_gnd)
        
        # Generate Parallel Interconnect Nodes (Ladder Rungs)
        for i in range(self.segments + 1):
            curr_x = start_x + pcbnew.FromMM(i * self.seg_len)
            
            # Vertical connection node bridging across rails
            rung = pcbnew.PCB_TRACK(self.board)
            rung.SetStart(pcbnew.VECTOR2I(curr_x, vcc_y))
            rung.SetEnd(pcbnew.VECTOR2I(curr_x, gnd_y))
            rung.SetWidth(self.node_width)
            rung.SetLayer(self.bottom_layer) # Placed on bottom layer to clear component footprints
            self.board.Add(rung)
            
        pcbnew.Refresh()
        print(f"Successfully generated {self.segments} parallel segments ({total_length}mm total length).")

# To execute:
# gen = RomulanTapeGenerator(segment_count=32, segment_length_mm=100.0)
# gen.generate_parallel_bus()
