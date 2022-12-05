import os

with open("TOKEN") as f:
    TOKEN = f.read().strip()

import logging
import requests
import uuid

from src.MemeEngine import MemeEngine
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

GET_FIRST_LINE, GET_SECOND_LINE, GET_PICTURE, START_ROUTES = range(4)


class Commands:
    CANCEL = "Передумал"
    MAKE_MEM = "Сделать мем"
    TEMPLATES = "Шаблоны"
    NOTHING = "ничего"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await update.message.reply_html(
        f"Привет, {user.username}! "
        f"Я бот который умеет делать надписи на фотографиях. "
        f"Присылай мне картинку и скажи что на ней написать. "
        f"Готовы шаблоны мемасиков: https://t.me/addstickers/memaker_templates",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM]], one_time_keyboard=True, resize_keyboard=True
        ),
    )


async def mem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Давай сделаем мемасик. Присылай картинку!",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.CANCEL], [Commands.TEMPLATES]], resize_keyboard=True
        ),
    )

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

    await update.message.reply_text(
        "Получил картину. Что напишем сверху?",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.CANCEL], [Commands.NOTHING]], resize_keyboard=True
        ),
    )

    return GET_FIRST_LINE


async def get_first_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["first_line"] = update.message.text
    if update.message.text == Commands.NOTHING:
        context.user_data["first_line"] = ""
    await update.message.reply_text("Понял. Что напишем внизу?")
    return GET_SECOND_LINE


async def get_second_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["second_line"] = update.message.text
    if update.message.text == Commands.NOTHING:
        context.user_data["second_line"] = ""
    path = MemeEngine(f"./tmp/{update.effective_user.username}").make_meme(
        context.user_data["picture_path"],
        context.user_data["first_line"].strip().upper(),
        context.user_data["second_line"].strip().upper(),
    )

    os.remove(context.user_data["picture_path"])

    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=path,
        caption="По-красоте...",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM]], one_time_keyboard=True, resize_keyboard=True
        ),
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Ок...",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM]], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    if context.user_data.get("picture_path"):
        os.remove(context.user_data["picture_path"])
    context.user_data.clear()
    return ConversationHandler.END


async def templates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text=f"Тут: https://t.me/addstickers/memaker_templates",
        reply_to_message_id=update.message.message_id,
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.Regex(Commands.TEMPLATES), templates)
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(Commands.MAKE_MEM), mem),
            ],
            states={
                GET_PICTURE: [
                    MessageHandler(filters.Regex(Commands.CANCEL), cancel),
                    MessageHandler(filters.ATTACHMENT, download_attachment),
                    MessageHandler(filters.FORWARDED, download_attachment),
                ],
                GET_FIRST_LINE: [
                    MessageHandler(filters.Regex(Commands.CANCEL), cancel),
                    MessageHandler(filters.TEXT, get_first_line),
                ],
                GET_SECOND_LINE: [
                    MessageHandler(filters.Regex(Commands.CANCEL), cancel),
                    MessageHandler(filters.TEXT, get_second_line),
                ],
            },
            fallbacks=[MessageHandler(filters.Regex(Commands.CANCEL), cancel)],
        ),
    )

    application.run_polling()


if __name__ == "__main__":
    main()
