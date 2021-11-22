from setuptools import setup

setup(
    name="digital-land web",
    version="0.1",
    long_description=__doc__,
    packages=["dl_web", "dl_web.routers"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "digital_land @ git+https://github.com/digital-land/digital-land-python.git#egg=digital-land",
        "digital_land_frontend @ git+https://github.com/digital-land/digital-land-frontend.git#egg=digital_land_frontend",
        "fastapi",
        "aiofiles",
        "uvicorn",
        "gunicorn",
        "jinja2",
        "aiohttp[speedups]",
        "PyYAML",
        "python-dotenv",
        "requests",
    ],
    extras_require={
        "testing": ["pytest", "flake8", "pre-commit", "playwright", "pytest-playwright", "black"]
    },
)
