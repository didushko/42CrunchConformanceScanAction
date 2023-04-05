from setuptools import setup, find_packages

setup(
    name="x42Crunch_python_sdk",
    version="0.1",
    py_modules=["x42crunch_python_sdk"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click"],
    entry_points={
        'console_scripts': [
            'xliic_scan = x42crunch_python_sdk.scripts.xliic_scan:_scan',
        ],
    },
)