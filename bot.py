import os

from telegram.constants import MenuButtonType

with open("TOKEN") as f:
    TOKEN = f.read().strip()

import logging
import requests
import uuid

from src.MemeEngine import MemeEngine
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MenuButton, KeyboardButton, \
    ReplyKeyboardMarkup, MenuButtonCommands
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler, CallbackQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GET_FIRST_LINE, GET_SECOND_LINE, GET_PICTURE, START_ROUTES = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    keyboard = [["Сделать мем"]]

    await update.message.reply_html(
        f"Привет, {user.username}! "
        f"Я бот который умеет делать надписи на фотографиях. "
        f"Используй /mem Присылай мне картинку и скажи что на ней написать.",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

    return GET_PICTURE


async def mem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Давай сделаем мемасик! Присылай картинку!")
    return GET_PICTURE


async def download_attachment(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    attachments = update.effective_message.effective_attachment
    attachment = attachments[-1] if type(attachments) == list else attachments
    file_info = await context.bot.get_file(file_id=attachment.file_id)
    response = requests.get(file_info.file_path, allow_redirects=True)
    os.makedirs(f"tmp/{update.effective_user.username}", exist_ok=True)
    tmp_file_path = f"tmp/{update.effective_user.username}/{uuid.uuid4()}.webp"
    open(tmp_file_path, "wb").write(response.content)
    context.user_data["picture_path"] = tmp_file_path
    await update.message.reply_text("Получил картину. Что напишем сверху?")
    return GET_FIRST_LINE


async def get_first_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["first_line"] = update.message.text
    await update.message.reply_text("Понял. Что напишем внизу?")
    return GET_SECOND_LINE


async def get_second_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["second_line"] = update.message.text
    path = MemeEngine(f"./tmp/{update.effective_user.username}").make_meme(
        context.user_data["picture_path"],
        context.user_data["first_line"].strip().upper(),
        context.user_data["second_line"].strip().upper(),
    )

    os.remove(context.user_data["picture_path"])

    keyboard = [["Сделать мем"]]

    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=path,
        caption="По-красоте...",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True
        )
    )
    context.user_data.clear()

    return ConversationHandler.END


# Tests
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Привет, ты сейчас в {update.message.location}")


async def dog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def get_url():
        contents = requests.get("https://random.dog/woof.json").json()
        url = contents["url"]
        return url

    await context.bot.send_photo(chat_id=update.message.chat_id, photo=get_url())


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Tests
    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(CommandHandler("dog", dog))

    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("mem", mem),
                MessageHandler(filters.Regex("Сделать мем"), mem)
            ],
            states={
                GET_PICTURE: [
                    MessageHandler(filters.ATTACHMENT, download_attachment),
                    MessageHandler(filters.FORWARDED, download_attachment),
                ],
                GET_FIRST_LINE: [
                    MessageHandler(filters.TEXT, get_first_line),
                ],
                GET_SECOND_LINE: [
                    MessageHandler(filters.TEXT, get_second_line),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),
    )

    application.run_polling()


if __name__ == "__main__":
    main()
