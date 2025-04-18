import telebot
from telebot import types
from pycoingecko import CoinGeckoAPI
from py_currency_converter import convert
import os 
import logging 

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cg = CoinGeckoAPI()

# --- Configuration ---
# It's better to get the token from environment variables for security
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7238971393:AAHHfuEo6CuLbVhx4TGaFHgrUIv_ALgZzkA') # Use provided token as fallback
# !!! IMPORTANT: Replace this with the ACTUAL URL where your game is hosted !!!
# Example: If hosted on GitHub Pages, it might look like https://your-username.github.io/your-repo-name/
GAME_URL = 'https://web.dger345.temp.swtest.ru' # <<< --- !!! REPLACE THIS WITH YOUR ACTUAL GAME URL !!!

if not BOT_TOKEN:
    logger.error("Error: Telegram Bot Token not found. Set TELEGRAM_BOT_TOKEN environment variable.")
    exit()
if GAME_URL == 'https://web.dger345.temp.swtest.ru':
    logger.warning("Warning: GAME_URL is set to the default placeholder. Replace it with your actual game URL.")


bot = telebot.TeleBot(BOT_TOKEN)

# --- Crypto Name Mapping (for consistency) ---
CRYPTO_MAP = {
    'bitcoin': ('Bitcoin', 'BTC', '🪙'),
    'ethereum': ('Ethereum', 'ETH', 'Ξ'),
    'litecoin': ('Litecoin', 'LTC', 'Ł'),
    'matic-network': ('Polygon', 'MATIC', '💜'),
    'uniswap': ('Uniswap', 'UNI', '🦄')
}

@bot.message_handler(commands=['start'])
def main(message):
    """Handles the /start command and shows the main menu."""
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    photo = 'https://i.pinimg.com/originals/0f/cc/ce/0fccce88d1a675f68294b626b30e009b.jpg'
    try:
        bot.send_photo(message.chat.id, photo, caption='Привет,я Курсовик!🤓')
    except telebot.apihelper.ApiException as e:
        logger.warning(f"Could not send photo: {e}. Sending text instead.")
        bot.send_message(message.chat.id, 'Привет,я Курсовик!🤓')

    # Add the "Игра 🎮" button here
    b1.add(types.KeyboardButton('Крипта💎'), types.KeyboardButton('Валюта💲'),
           types.KeyboardButton('Калькулятор🧮'), types.KeyboardButton('Игра 🎮'))
    bot.send_message(message.chat.id, 'Ну что юный крипто-арбитражник,что тебе интересно?😏', reply_markup=b1)
    bot.register_next_step_handler(message, step)

def step(message):
    """Routes user from the main menu."""
    if message.text == 'Крипта💎':
        step2(message) # Go to crypto menu
    elif message.text == 'Валюта💲':
        fiat(message) # Go to fiat menu
    elif message.text == 'Калькулятор🧮':
        convert1(message) # Go to calculator menu
    elif message.text == 'Игра 🎮':
        send_game_link(message) # Go to game link sender
    elif message.text == 'Назад': # Allow 'Назад' from anywhere to return to main
        main(message)
    else:
        # Handle unexpected input at the main menu level
        b1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1.add(types.KeyboardButton('Крипта💎'), types.KeyboardButton('Валюта💲'),
               types.KeyboardButton('Калькулятор🧮'), types.KeyboardButton('Игра 🎮'))
        bot.send_message(message.chat.id, "Пожалуйста, выбери опцию из меню.", reply_markup=b1)
        bot.register_next_step_handler(message, step) # Re-register for main menu choice

# --- Game Section ---
def send_game_link(message):
    """Sends an inline button linking to the web game."""
    if GAME_URL == 'https://web.dger345.temp.swtest.ru':
        bot.send_message(message.chat.id,
                         "⚠️ **Game URL not configured!** Please ask the bot administrator to set the `GAME_URL` in the bot's code.")
        main(message) # Go back to main menu
        return

    markup = types.InlineKeyboardMarkup()
    game_button = types.InlineKeyboardButton(text="🚀 Запустить Игру! 🚀", url=GAME_URL)
    markup.add(game_button)

    bot.send_message(message.chat.id,
                     f"Нажми кнопку ниже, чтобы запустить игру!\n\n"
                     f"⚠️ Убедись, что открываешь ссылку в браузере.\n\n"
                     f"🔗 {GAME_URL}",
                     reply_markup=markup)
    # After sending the link, show the main keyboard again
    main(message) # Go back to main menu


# --- Fiat Currency Section ---
def fiat(message):
    """Shows the fiat currency selection menu."""
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) # Use row_width for better layout
    b1.add(types.KeyboardButton('Курс доллара💲'), types.KeyboardButton('Курс рубля ₽'),
           types.KeyboardButton('Назад')) # Add Back button
    q = bot.send_message(message.chat.id, 'Арбитраж все дела😏 Выбери валюту:', reply_markup=b1)
    bot.register_next_step_handler(q, fiat_step2)

def fiat_step2(message):
    """Processes fiat currency choice and displays rates."""
    if message.text == "Курс доллара💲":
        get_fiat_rates(message, 'USD')
    elif message.text == "Курс рубля ₽":
        get_fiat_rates(message, 'RUB')
    elif message.text == 'Назад':
        main(message) # Go back to main menu
    else:
        # Invalid input in this menu
        bot.send_message(message.chat.id, "Пожалуйста, выбери опцию из меню или нажми 'Назад'.")
        bot.register_next_step_handler(message, fiat_step2) # Ask again

def get_fiat_rates(message, base_currency):
    """Fetches and displays fiat rates for the selected base currency."""
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1.add(types.KeyboardButton('Назад')) # Only Back button needed after showing results

    target_currencies = ['RUB', 'EUR', 'UAH', 'KZT', 'USD']
    target_currencies = [c for c in target_currencies if c != base_currency] # Remove base from targets

    try:
        rates = convert(base=base_currency, amount=1, to=target_currencies)
        logger.info(f"Fetched fiat rates for {base_currency}: {rates}")

        text = f"Курс для 1 {base_currency}:\n\n"
        reply_msg = "Вот текущие курсы:" # Default reply

        if base_currency == 'USD':
            text += (f'🇺🇸 1 USD ≈ {rates.get("RUB", "N/A"):.2f} RUB\n'
                     f'🇺🇸 1 USD ≈ {rates.get("EUR", "N/A"):.2f} EUR\n'
                     f'🇺🇸 1 USD ≈ {rates.get("UAH", "N/A"):.2f} UAH\n'
                     f'🇺🇸 1 USD ≈ {rates.get("KZT", "N/A"):.2f} KZT')
            reply_msg = 'Ну что-то не густо😔'
        elif base_currency == 'RUB':
            text += (f'🇷🇺 1 RUB ≈ {rates.get("USD", "N/A"):.4f} USD\n'
                     f'🇷🇺 1 RUB ≈ {rates.get("EUR", "N/A"):.4f} EUR\n'
                     f'🇷🇺 1 RUB ≈ {rates.get("UAH", "N/A"):.2f} UAH\n'
                     f'🇷🇺 1 RUB ≈ {rates.get("KZT", "N/A"):.2f} KZT')
            reply_msg = 'Ну что то тоже не очень 😔'
        else: # Fallback for other currencies if added
            for currency, rate in rates.items():
                 # Ensure rate is formatted correctly, handle potential errors
                 try:
                     formatted_rate = f"{float(rate):.2f}"
                 except (ValueError, TypeError):
                     formatted_rate = "N/A"
                 text += f"1 {base_currency} ≈ {formatted_rate} {currency}\n"


        bot.send_message(message.chat.id, text.strip()) # Send the rates
        # Ask to go back or choose again
        go_back_msg = bot.send_message(message.chat.id, reply_msg, reply_markup=b1)
        # Reregister fiat handler to allow choosing another currency or going back
        bot.register_next_step_handler(go_back_msg, fiat) # Go back to the fiat menu selection

    except Exception as e: # Catch broader exceptions from the API call
        logger.error(f"Error fetching/processing fiat rates for {base_currency}: {e}")
        bot.send_message(message.chat.id, f'😔 Ошибка получения курса для {base_currency}. Попробуйте позже.')
        # Still offer to go back or try again
        go_back_msg = bot.send_message(message.chat.id, 'Вернуться в меню валют?', reply_markup=b1)
        bot.register_next_step_handler(go_back_msg, fiat) # Go back to the fiat menu selection


# --- Crypto Currency Section ---
def step2(message):
    """Shows the crypto display currency selection menu."""
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1.add(types.KeyboardButton('Курс в долларах💲'), types.KeyboardButton('Курс в рублях ₽'),
           types.KeyboardButton('Назад'))
    q_main = bot.send_message(message.chat.id, 'Арбитражник выбирай😎 Валюту для отображения курса:', reply_markup=b1)
    bot.register_next_step_handler(q_main, step3)

def step3(message):
    """Processes crypto display currency choice and shows rates."""
    if message.text == 'Курс в долларах💲':
        get_crypto_prices(message, 'usd')
    elif message.text == 'Курс в рублях ₽':
        get_crypto_prices(message, 'rub')
    elif message.text == 'Назад':
        main(message) # Go back to main menu
    else:
         # Invalid input in this menu
        bot.send_message(message.chat.id, "Пожалуйста, выбери опцию из меню или нажми 'Назад'.")
        bot.register_next_step_handler(message, step3) # Ask again

def get_crypto_prices(message, vs_currency):
    """Fetches and displays crypto prices in the chosen fiat currency."""
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1.add(types.KeyboardButton('Назад')) # Only Back button needed after showing results

    crypto_ids = ','.join(CRYPTO_MAP.keys()) # Get IDs from our map
    currency_symbol = '$' if vs_currency == 'usd' else '₽'
    reply_msg = 'Опять упала ??!?!?🤬' if vs_currency == 'usd' else 'В рублях покрасивее да??😎'

    try:
        prices = cg.get_price(ids=crypto_ids, vs_currencies=vs_currency)
        logger.info(f"Fetched crypto prices in {vs_currency}: {prices}")

        text = f'Курс криптовалют в {vs_currency.upper()}:\n\n'
        for coin_id, data in prices.items():
            if coin_id in CRYPTO_MAP:
                name, symbol, emoji = CRYPTO_MAP[coin_id]
                price = data.get(vs_currency)
                # Format price with commas and decimals
                try:
                    formatted_price = f"{float(price):,.2f}" if price is not None else "N/A"
                except (ValueError, TypeError):
                    formatted_price = "N/A"
                text += f'{emoji} {name} ({symbol}) ≈ {formatted_price} {currency_symbol}\n'
            else:
                logger.warning(f"Received unexpected coin_id '{coin_id}' from API.")


        bot.send_message(message.chat.id, text.strip())
        # Ask to go back or choose again
        go_back_msg = bot.send_message(message.chat.id, reply_msg, reply_markup=b1)
        # Reregister step2 handler to allow choosing another currency or going back
        bot.register_next_step_handler(go_back_msg, step2) # Go back to crypto menu selection

    except Exception as e: # Catch broader exceptions
        logger.error(f"Error fetching/processing crypto prices ({vs_currency}): {e}")
        bot.send_message(message.chat.id, f'😔 Ошибка получения курса к {vs_currency.upper()}. Попробуйте позже.')
        # Still offer to go back or try again
        go_back_msg = bot.send_message(message.chat.id, 'Вернуться в меню криптовалют?', reply_markup=b1)
        bot.register_next_step_handler(go_back_msg, step2) # Go back to crypto menu selection


# --- Calculator Section ---
def convert1(message):
    """Shows the calculator crypto selection menu."""
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) # Use row_width
    # Get button names from CRYPTO_MAP
    buttons = [types.KeyboardButton(f"{CRYPTO_MAP[cid][2]} {CRYPTO_MAP[cid][0]}") for cid in CRYPTO_MAP]
    b1.add(*buttons) # Add crypto buttons
    b1.add(types.KeyboardButton('Назад')) # Add Back button on its own row
    msg = bot.send_message(message.chat.id, 'Что будем считать брат?🫡 Выбери крипту:', reply_markup=b1)
    bot.register_next_step_handler(msg, convert2)

def convert2(message):
    """Processes the chosen crypto and asks for the amount."""
    # Find the selected crypto based on button text (including emoji)
    selected_coin_id = None
    selected_coin_symbol = None
    prompt_msg = None

    for coin_id, (name, symbol, emoji) in CRYPTO_MAP.items():
        if message.text == f"{emoji} {name}":
            selected_coin_id = coin_id
            selected_coin_symbol = symbol
            # Use more specific prompts per coin if desired, or a generic one
            # Example using specific prompts similar to the original code:
            if coin_id == 'bitcoin': prompt_msg = 'Сколько битков посчитать чтоб афигеть от цифр?😈'
            elif coin_id == 'ethereum': prompt_msg = 'Эфир сила брат, считать то сколько будем?🧐'
            elif coin_id == 'litecoin': prompt_msg = 'Что то менее популярная крипта, сколько считать?😁'
            elif coin_id == 'matic-network': prompt_msg = 'Решил и его посчитать?! Не мешаю брат, ты только число скажи😁'
            elif coin_id == 'uniswap': prompt_msg = 'Сколько нн крипты будем считать?🧐'
            else: prompt_msg = f'Сколько {symbol} будем считать?' # Fallback prompt
            break

    if selected_coin_id and selected_coin_symbol and prompt_msg:
        # Ask for the amount, removing the keyboard for number input
        # Pass coin details to the next step
        msg = bot.send_message(message.chat.id, prompt_msg, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, calculate_crypto_value, selected_coin_id, selected_coin_symbol)
    elif message.text == 'Назад':
        main(message) # Go back to main menu
    else:
        # Invalid selection
        bot.send_message(message.chat.id, "Пожалуйста, выбери криптовалюту из списка или нажми 'Назад'.")
        # Re-show the calculator menu
        bot.register_next_step_handler(message, convert1)

def calculate_crypto_value(message, coin_id, coin_symbol):
    """Calculates the USD value of the entered crypto amount."""
    try:
        # Allow comma or dot as decimal separator, handle potential spaces
        amount_str = message.text.strip().replace(',', '.')
        amount = float(amount_str)

        if amount <= 0: # Check for non-positive amount
             bot.send_message(message.chat.id, '❌ Количество должно быть положительным числом.')
             # Go back to calculator coin selection
             main(message) # Go back to main menu after error message
             return

        # Fetch the current price in USD
        price_data = cg.get_price(ids=coin_id, vs_currencies='usd')
        logger.info(f"Fetched price for {coin_id}: {price_data}")

        # Check if API response is valid
        if coin_id not in price_data or 'usd' not in price_data[coin_id]:
            raise ValueError(f"Could not find USD price for {coin_id} in API response.")

        price_usd = price_data[coin_id]['usd']
        total_value = price_usd * amount

        # Format output nicely using f-string formatting for thousands separators
        emoji = CRYPTO_MAP[coin_id][2]
        bot.send_message(message.chat.id,
                         f'{emoji} {amount:,.4f} {coin_symbol} ≈ ${total_value:,.2f} USD')
        # Return to main menu after successful calculation
        main(message)

    except ValueError as ve:
        # Handle invalid number input specifically
        logger.warning(f"Invalid number input for {coin_symbol} calculation: {message.text} - {ve}")
        bot.send_message(message.chat.id, '❌ Пожалуйста, введите числовое значение (например, 0.5 или 10).')
        # Ask for the amount *again* for the *same* coin
        msg = bot.send_message(message.chat.id, f'Попробуй еще раз, сколько {coin_symbol} будем считать?')
        bot.register_next_step_handler(msg, calculate_crypto_value, coin_id, coin_symbol)

    except Exception as e:
        # Handle API errors or other unexpected issues
        logger.error(f"Error calculating crypto value ({coin_id}): {e}")
        bot.send_message(message.chat.id, f'😔 Не удалось посчитать стоимость для {coin_symbol}. Попробуйте позже.')
        # Return to main menu on API or other errors
        main(message)

# --- Fallback Handler ---
# This should catch any text messages not handled by register_next_step_handler
# or the main menu handler `step`
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_unknown_text(message):
    """Handles any text messages that don't match other handlers."""
    logger.info(f"Received unhandled text message: {message.text}")
    bot.send_message(message.chat.id, "Извини, не понял тебя. Пожалуйста, используй кнопки меню.")
    # Send back to the main menu
    main(message)


# --- Start Polling ---
if __name__ == '__main__':
    logger.info("Bot starting polling...")
    try:
        # Use infinity_polling with error handling recommended by pyTelegramBotAPI
        bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=5)
    except Exception as e:
        logger.critical(f"Bot polling encountered a critical error: {e}", exc_info=True)
    finally:
        logger.info("Bot stopped.")