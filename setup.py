import cx_Freeze

executables = [cx_Freeze.Executable("Racey.py")]

cx_Freeze.setup(
    name="Racey",
    options={
        "build_exe": {
            "packages": ["pygame"],  # List any packages your script requires
            "include_files": ["pictures/Racey.png"],  # Any external you want to include
            "optimize": 2  # Optional: optimization level for the build (helps with performance)
        }
    },
    executables=executables
)