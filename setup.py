from setuptools import setup, find_packages

setup(
    name='imva',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
    ],
    entry_points={
        'console_scripts': [
            'imva=imva.app:main'
        ]
    }
)

