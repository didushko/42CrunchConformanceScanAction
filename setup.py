from setuptools import setup

setup(
    name="cicd_python",
    version="1.0.0",
    packages=["cicd_python"],
    entry_points={
        "console_scripts": [
            "runScan = cicd_python.runScan:main"
        ]
    }
)