// romulan_cargo_stabilizer.scad
// OpenSCAD Parametric Script for Anti-Wobble Transport System

$fn = 100;

// Set parameter to true to render the square sabot; false to render the ramp guide track
render_sabot = true; 

barrel_radius = 300;      // 600mm diameter barrel
sabot_wall = 25;          // Heavy protective outer wall
sabot_height = 150;       // Structural pocket depth
guide_rail_width = 700;   // Outer width of the ramp board path
clearance = 5;            // Structural tolerances

if (render_sabot) {
    target_square_sabot();
} else {
    ramp_guide_board_channel();
}

module target_square_sabot() {
    difference() {
        // Main Square Body (The Tetris Block Footprint)
        size = (barrel_radius * 2) + (sabot_wall * 2);
        translate([-size/2, -size/2, 0])
            cube([size, size, sabot_height]);
        
        // Cylindrical cutout for the industrial barrel
        translate([0, 0, sabot_wall])
            cylinder(r=barrel_radius + clearance, h=sabot_height);
            
        // Lower tracking channels to lock into the tape track and prevent spinning
        translate([-size/2 - 1, -40, -1])
            cube([size + 2, 80, sabot_wall + 2]);
    }
}

module ramp_guide_board_channel() {
    difference() {
        // Base board backing
        translate([-guide_rail_width/2, -500, 0])
            cube([guide_rail_width, 1000, 40]);
            
        // Center channel cutout where the Eddy-Tape lays flush
        translate([-150, -501, 20])
            cube([300, 1002, 25]);
            
        // Left and Right safety interlock slots to capture the sabot base edges
        translate([-(guide_rail_width/2 - 20), -501, 15])
            cube([50, 1002, 30]);
        translate([(guide_rail_width/2 - 70), -501, 15])
            cube([50, 1002, 30]);
    }
}
