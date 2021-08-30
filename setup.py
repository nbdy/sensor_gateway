from setuptools import setup, find_packages


setup(
    long_description=open("README.md", "r").read(),
    name="sensor_gateway",
    version="0.2",
    description="sensor gateway for data collection",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/nbdy/sensor_gateway",
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License'
    ],
    keywords="sensor gateway data collection",
    packages=find_packages(),
    install_requires=[
        "flask", "pyserial", "procpy==0.4", "dataset", "pyrunnable", "loguru", "simplejson", "psycopg2-binary"
    ],
    entry_points={
        'console_scripts': [
            'sensor_gateway = sensor_gateway.__main__:main'
        ]
    },
    long_description_content_type="text/markdown",
)