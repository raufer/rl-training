import os
import logging


console_format ='%(asctime)s, %(name)s[:%(lineno)d], %(levelname)-4s - %(message)s'

logging.basicConfig(
    format=console_format,
    level=logging.INFO
)

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
