using System;
using System.IO;
using System.Linq;

class Program {
    static void Main(string[] args) {
        string[] files = {
            "standing_wave_closed_pipe.gp",
            "standing_wave_formation.gp",
            "standing_wave_open_pipe.gp",
            "standing_wave_string_fixed.gp",
            "standing_wave_string_harmonics.gp",
            "wave_interference_3d.gp",
            "wave_interference_topdown.gp"
        };
        foreach (var file in files) {
            if (!File.Exists(file)) continue;
            byte[] bytes = File.ReadAllBytes(file);
            if (bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF) {
                Console.WriteLine($"Removing BOM from {file}");
                File.WriteAllBytes(file, bytes.Skip(3).ToArray());
            } else {
                Console.WriteLine($"No BOM found in {file}");
            }
        }
    }
}
