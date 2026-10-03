"""
limiter.py
----------
The slowapi rate limiter instance, split into its own module so both
main.py (which registers it on the app) and routers/contact.py (which
applies it to a route) can import the same object without a circular
import between them.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
