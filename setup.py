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
    version='0.0.0',
    author='Aykut Kabaoglu',
    author_email='aykutkabaoglu@gmail.com',
    license='MIT',
    description='Provides modules to create plotly figures and dash apps from ROS bag files.',
    url='https://github.com/aykutkabaoglu/rosbag-dash',
    )
