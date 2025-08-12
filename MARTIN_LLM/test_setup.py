# test_setup.py
from cx_Freeze import setup, Executable

setup(
    name="TestApp",
    version="1.0",
    description="Prueba",
    options={"build_exe": {"include_msvcrt": True}},
    executables=[Executable("run.py")]
)
