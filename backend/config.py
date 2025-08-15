import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# Templates Jinja2
templates = Jinja2Templates(directory="frontend/templates")