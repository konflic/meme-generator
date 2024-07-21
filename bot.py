import datetime
import os

with open("TOKEN") as f:
    TOKEN = f.read().strip()

import requests
import uuid
import pathlib

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
    CANCEL = "/отмена"
    MAKE_MEM = "/мем"
    MAKE_DEMOTIVATOR = "/демотиватор"
    TEMPLATES = "/шаблоны"
    NOTHING = "/ничего"
    PRIVACY = "/privacy"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await update.message.reply_html(
        f"Привет, {user.username}! Я бот для создания мемасиков!\n"
        f"Используй команды \u2B07 и следуй моим подсказкам.",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM, Commands.MAKE_DEMOTIVATOR]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )


async def mem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Давай сделаем мемасик. Присылай картинку!\nПерешли из другого чата, загрузи свою или бери из шаблонов \u2B07",
        reply_markup=ReplyKeyboardMarkup(
            [
                [Commands.TEMPLATES],
                [Commands.CANCEL],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
        read_timeout=30,
        pool_timeout=30
    )
    return GET_PICTURE


async def demotivator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Давай замутим демотиватор. Присылай картинку!",
        reply_markup=ReplyKeyboardMarkup(
            [
                [Commands.CANCEL],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
        read_timeout=30,
        pool_timeout=30
    )
    return GET_PICTURE


async def download_attachment(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_message.photo or update.effective_message.sticker:
        attachments = update.effective_message.effective_attachment
        attachment = attachments[-1] if type(attachments) == tuple else attachments
        file_info = await context.bot.get_file(file_id=attachment.file_id)

        response = requests.get(file_info.file_path, allow_redirects=True)

        os.makedirs(f"tmp/{update.effective_user.username}", exist_ok=True)
        tmp_file_path = f"tmp/{update.effective_user.username}/{uuid.uuid4()}.webp"

        open(tmp_file_path, "wb+").write(response.content)
        context.user_data["picture_path"] = tmp_file_path

        await update.message.reply_text(
            "Получил картину. Что напишем сверху?\nЕсли оставим пустым то жми /ничего \u2B07",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [Commands.NOTHING],
                    [Commands.CANCEL],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
            read_timeout=30,
            pool_timeout=30
        )

        return GET_FIRST_LINE


async def get_first_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["first_line"] = update.message.text

    if update.message.text == Commands.NOTHING:
        context.user_data["first_line"] = ""

    await update.message.reply_text(
        "Понял. Что напишем внизу?\nЕсли оставим пустым то жми /ничего \u2B07",
        reply_markup=ReplyKeyboardMarkup(
            [
                [Commands.NOTHING],
                [Commands.CANCEL],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
        pool_timeout=30,
        read_timeout=30
    )

    return GET_SECOND_LINE


async def get_second_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["second_line"] = update.message.text

    if update.message.text == Commands.NOTHING:
        context.user_data["second_line"] = ""

    path = MemeEngine(f"./tmp/{update.effective_user.username}").make_meme(
        context.user_data["picture_path"],
        context.user_data["first_line"].strip(),
        context.user_data["second_line"].strip(),
    )

    os.remove(context.user_data["picture_path"])

    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=path,
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM, Commands.MAKE_DEMOTIVATOR]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
        read_timeout=30,
        pool_timeout=30
    )

    await context.bot.send_message(
        chat_id=156109367, text=f"@{update.effective_user.username} just created a meme!"
    )

    context.user_data.clear()
    return ConversationHandler.END


async def get_second_demotivator_line(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["second_line"] = update.message.text

    if update.message.text == Commands.NOTHING:
        context.user_data["second_line"] = ""

    path = MemeEngine(f"./tmp/{update.effective_user.username}").make_demotivator(
        context.user_data["picture_path"],
        context.user_data["first_line"].strip(),
        context.user_data["second_line"].strip(),
    )

    os.remove(context.user_data["picture_path"])

    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=path,
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM, Commands.MAKE_DEMOTIVATOR]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
        read_timeout=30,
        pool_timeout=30
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Ок...",
        reply_markup=ReplyKeyboardMarkup(
            [[Commands.MAKE_MEM, Commands.MAKE_DEMOTIVATOR]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
        read_timeout=30,
        pool_timeout=30
    )
    if context.user_data.get("picture_path"):
        os.remove(context.user_data["picture_path"])
    context.user_data.clear()

    return ConversationHandler.END


async def templates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="https://t.me/addstickers/memaker_templates\nhttps://t.me/addstickers/memaker_templates2",
        reply_to_message_id=update.message.message_id,
        read_timeout=30,
        pool_timeout=30
    )


async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == "s_amurai":
        for file in pathlib.Path("./tmp/").resolve().rglob("*"):
            if file.is_dir():
                response = f"{file.name} [{len(list(file.iterdir()))}] last:"
                latest_file = max(file.iterdir(), key=os.path.getctime)
                response += f" {datetime.datetime.fromtimestamp(latest_file.stat().st_ctime).strftime('%Y-%m-%d')}"
                await update.message.reply_text(response, disable_notification=True)


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="Bot does not collect, proceed or store any personal data.",
        reply_to_message_id=update.message.message_id,
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("secret", admin_list))
    application.add_handler(CommandHandler("privacy", privacy))

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

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(Commands.MAKE_DEMOTIVATOR), demotivator),
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
                    MessageHandler(filters.TEXT, get_second_demotivator_line),
                ],
            },
            fallbacks=[MessageHandler(filters.Regex(Commands.CANCEL), cancel)],
        ),
    )

    application.add_handler(
        MessageHandler(filters.TEXT, start)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
