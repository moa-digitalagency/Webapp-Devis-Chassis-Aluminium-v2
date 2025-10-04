#!/usr/bin/env python3
"""
Tailwind CSS Build Script - 100% Python (No Node.js)
Uses standalone Tailwind binary for CSS compilation
"""
import subprocess
import sys
import os
from pathlib import Path

def build_css(minify=True, watch=False):
    """
    Compile Tailwind CSS using the standalone binary
    """
    input_file = "app/static/css/tailwind-input.css"
    output_file = "app/static/css/tailwind.css"
    tailwind_binary = "./tailwindcss"
    
    if not os.path.exists(tailwind_binary):
        print(f"❌ Error: Tailwind binary not found at {tailwind_binary}")
        print("   Download from: https://github.com/tailwindlabs/tailwindcss/releases")
        sys.exit(1)
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)
    
    cmd = [tailwind_binary, "-i", input_file, "-o", output_file]
    
    if minify:
        cmd.append("--minify")
    
    if watch:
        cmd.append("--watch")
    
    print(f"🎨 Tailwind CSS Build (Python)")
    print(f"   Input:  {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Minify: {'Yes' if minify else 'No'}")
    print(f"   Watch:  {'Yes' if watch else 'No'}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        if not watch:
            file_size = Path(output_file).stat().st_size / 1024
            print(f"✅ CSS compiled successfully! ({file_size:.1f}KB)")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⏹️  Watch mode stopped")
        return 0

if __name__ == "__main__":
    watch_mode = "--watch" in sys.argv or "-w" in sys.argv
    no_minify = "--no-minify" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
🎨 Tailwind CSS Build Tool (Python)

Usage: python build_css.py [options]

Options:
  --watch, -w      Watch for changes and rebuild automatically
  --no-minify      Don't minify the output CSS
  --help, -h       Show this help message

Examples:
  python build_css.py              # Build once, minified
  python build_css.py --watch      # Watch mode
  python build_css.py --no-minify  # Build without minification

Note: This script uses the standalone Tailwind binary (no Node.js required)
        """)
        sys.exit(0)
    
    sys.exit(build_css(minify=not no_minify, watch=watch_mode))
