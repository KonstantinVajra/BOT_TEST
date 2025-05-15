from setuptools import setup, find_packages

setup(
    name="telegram-review-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.9",
        "telebot>=0.0.5",
        "SQLAlchemy>=2.0.23",
        "alembic>=1.12.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-asyncio>=0.21.1",
            "freezegun>=1.2.2",
        ],
    },
) 