#!/usr/bin/env python3
"""
Univac System Interface Bridge & Infrastructure Module
Integrates industrial data protocols with modern physical routing controls.
"""

import json

class UnivacLogisticsBridge:
    def __init__(self):
        """Initializes the data translation matrix for structural routing."""
        # Active manifest for military industrial materials tracking
        self.active_manifest = {}

    def format_legacy_record(self, asset_id, material, un_num, weight, footprint):
        """
        Translates modern tracking properties into an aligned text layout
        suitable for processing by legacy inventory systems.
        """
        # Ensure strict string lengths to match historical data columns
        field_id       = f"{asset_id:<12}"[:12]
        field_mat      = f"{material:<20}"[:20]
        field_un       = f"{un_num:<8}"[:8]
        field_weight   = f"{int(weight):06d}"
        field_foot     = f"{footprint:<6}"[:6]
        
        # Combine fields into a unified transaction string
        legacy_string = f"TX-{field_id}-{field_mat}-{field_un}-{field_weight}-{field_foot}"
        return legacy_string

    def register_cargo(self, asset_id, material, un_num, weight, footprint):
        """Appends verified logistics data to the system tracking manifest."""
        self.active_manifest[asset_id] = {
            "material_desc": material,
            "un_identifier": un_num,
            "mass_kilograms": float(weight),
            "base_geometry": footprint,
            "legacy_telemetry": self.format_legacy_record(asset_id, material, un_num, weight, footprint)
        }
        return self.active_manifest[asset_id]["legacy_telemetry"]

# Execution Test
bridge = UnivacLogisticsBridge()
card_output = bridge.register_cargo("BARREL_0x0A1", "Cobalt-60 Isotopes", "UN2916", 450, "0x04")
print("=== Legacy Interface Output ===")
print(card_output)
