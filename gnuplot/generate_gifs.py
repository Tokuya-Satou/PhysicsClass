import os
import subprocess

files = [
    'standing_wave_closed_pipe.gp',
    'standing_wave_formation.gp',
    'standing_wave_open_pipe.gp',
    'standing_wave_string_fixed.gp',
    'standing_wave_string_harmonics.gp',
    'wave_interference_3d.gp',
    'wave_interference_topdown.gp',
    'beats.gp',
    'doppler_effect.gp',
    'huygens_principle.gp',
    'longitudinal_wave.gp',
    'refraction_snell.gp'
]

for f in files:
    if not os.path.exists(f):
        print(f"Skipping {f} (not found)")
        continue
    
    print(f"Processing {f}...")
    with open(f, 'rb') as source:
        content = source.read()
        
    # Remove UTF-8 BOM if present
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
    
    # Write to a temporary file ensuring NO BOM
    temp_name = f + ".temp"
    with open(temp_name, 'wb') as temp:
        temp.write(content)
        
    try:
        subprocess.run(['gnuplot', temp_name], check=True)
        print(f"Successfully generated GIF for {f}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {f}: {e}")
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)
