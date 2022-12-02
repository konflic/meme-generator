import os

with open("TOKEN") as f:
    TOKEN = f.read()

import logging
import requests
import uuid

from src.MemeEngine import MemeEngine
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GET_FIRST_LINE, GET_SECOND_LINE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! "
        f"Я бот который умеет делать надписи на фотографиях. "
        f"Присылай мне картинку и скажи что на ней написать.",
    )


async def dog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def get_url():
        contents = requests.get("https://random.dog/woof.json").json()
        url = contents["url"]
        return url

    await context.bot.send_photo(chat_id=update.message.chat_id, photo=get_url())


async def download_attachment(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    attachments = update.effective_message.effective_attachment
    attachment = attachments[-1] if type(attachments) == list else attachments
    file_info = await context.bot.get_file(file_id=attachment.file_id)
    response = requests.get(file_info.file_path, allow_redirects=True)

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
        context.user_data["first_line"].strip(),
        context.user_data["second_line"].strip(),
    )

    os.remove(context.user_data["picture_path"])

    await context.bot.send_photo(
        chat_id=update.message.chat_id, photo=path, caption="По-красоте..."
    )
    context.user_data.clear()
    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data.clear()
    await update.message.reply_text("Ничего не понял. Давай потом!")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dog", dog))

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.ATTACHMENT, download_attachment),
                MessageHandler(filters.FORWARDED, download_attachment),
            ],
            states={
                GET_FIRST_LINE: [
                    MessageHandler(filters.TEXT, get_first_line),
                ],
                GET_SECOND_LINE: [
                    MessageHandler(filters.TEXT, get_second_line),
                ],
            },
            fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        ),
    )

    application.run_polling()


if __name__ == "__main__":
    main()
