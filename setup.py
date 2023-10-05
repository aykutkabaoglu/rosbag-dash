import setuptools

required_packages=[
        'numpy',
        'pycryptodomex',
        'pyyaml',
        'rospkg',
        'ipython',
        'gnupg',
        'pandas',
        'setuptools-scm',
        'importlib-resources',
        'plotly',
        'dash',
        'scipy'
        ]

setuptools.setup(
    name='rosbag_dash',
    packages=setuptools.find_packages(),
    install_requires=required_packages,
    )