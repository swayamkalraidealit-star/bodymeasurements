"""
Test to understand the measurement calculation issue

Looking at the measurement calculator, it's using these formulas:
- Chest: shoulder_width * 2.9
- Waist: hip_width * 2.8
- Hip: hip_width * 3.0

This is problematic because:
1. Chest circumference should be calculated from chest width, not shoulder width
2. The multipliers don't account for gender differences
3. Real body measurements don't scale linearly

Example issue:
- A male with shoulder_width = 46cm
- Chest = 46 * 2.9 = 133.4cm (WAY TOO LARGE!)
- Actual chest for size M = ~97cm

The issue is that the code is treating PIXEL DISTANCES as if they were actual widths,
and then multiplying by circumference ratios.

Real issue: The measurement calculator uses shoulder distance for chest,
but that's not correct - it should use a different landmark or estimation.
"""

print(__doc__)

# Simulate what's happening
shoulder_width_cm = 46  # Typical M size shoulderwidth
waist_width_cm = 30  # Approximate front-to-front hip width
hip_width_cm = 32  # Approximate hip width

# Current calculation
calculated_chest = shoulder_width_cm * 2.9
calculated_waist = waist_width_cm * 2.8
calculated_hip = hip_width_cm * 3.0

print("CURRENT FLAWED CALCULATIONS:")
print(f"Shoulder width (input): {shoulder_width_cm} cm")
print(f"Calculated chest: {calculated_chest:.1f} cm (WRONG - should be ~97cm for M)")
print(f"\nWaist width (input): {waist_width_cm} cm")
print(f"Calculated waist: {calculated_waist:.1f} cm")
print(f"\nHip width (input): {hip_width_cm} cm")
print(f"Calculated hip: {calculated_hip:.1f} cm")

print("\n" + "="*80)
print("THE REAL PROBLEM:")
print("="*80)
print("""
The measurement calculator is measuring the DISTANCE BETWEEN SHOULDERS
and calling it 'shoulder_width', then using that to calculate chest.

This is wrong because:
1. Shoulder distance ≠ Chest width
2. The code is at line 209-217:
   chest_width_px = distance(left_shoulder, right_shoulder)
   chest_width_cm = pixels_to_cm(chest_width_px, calibration_factor)
   measurements['chest'] = chest_width_cm * 2.9

This means it's:
   chest_circumference = shoulder_distance * 2.9

Which makes no sense anatomically!

SOLUTION:
We need to use DIFFERENT landmarks for chest measurement, or use a proper
anatomical model that accounts for body depth and proportions based on gender.
""")
