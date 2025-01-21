from telegram.ext import filters
from handlers.common import Keyboard


int_pattern = f"^\d+$"
float_pattern = r"^-?\d+\.\d+$"
char_pattern = f'[A-Za-z]'


cancel_filter = filters.Regex(f"/cancel")
back_filter = filters.Regex(f'{Keyboard.BACK.value}')
char_filter = filters.Regex(char_pattern)
int_filter = filters.Regex(int_pattern)
float_filter = filters.Regex(float_pattern)
number_filter = int_filter | float_filter
