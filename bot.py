import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# ==============================
# НАСТРОЙКИ — ЗАПОЛНИТЕ ЭТО!
# ==============================
BOT_TOKEN = "8767854896:AAHbnxyRkXWWB1FNZw2Vyc_XrNwJ4ljic4k"   # Токен от @BotFather
ADMIN_ID = 7691899663            # Ваш Chat ID (узнать у @userinfobot)
# ==============================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_map = {}


def escape(text: str) -> str:
    """Экранирует спецсимволы для MarkdownV2"""
    chars = r'_*[]()~`>#+-=|{}.!'
    for c in chars:
        text = text.replace(c, f'\\{c}')
    return text


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer(
        "👋 Привет! Напишите ваше сообщение, и мы ответим вам как можно скорее.\n"
        "Вы можете отправить текст, фото или файл.\n\n"
        "👋 Hello! Send your message and we will reply as soon as possible.\n"
        "You can send text, photo or file."
    )


@dp.message(Command("help"))
async def help_cmd(msg: Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer(
            "📋 Команды админа:\n"
            "Чтобы ответить пользователю — просто ответьте (Reply) на его сообщение.\n\n"
            "Бот автоматически перешлёт ваш ответ пользователю."
        )
    else:
        await msg.answer("Напишите ваш вопрос и мы ответим!")


@dp.message(F.chat.id == F.from_user.id)
async def handle_message(msg: Message):

    # === ОТВЕТ АДМИНА ПОЛЬЗОВАТЕЛЮ ===
    if msg.from_user.id == ADMIN_ID and msg.reply_to_message:
        replied_id = msg.reply_to_message.message_id
        target_chat = user_map.get(replied_id)

        if target_chat:
            try:
                if msg.text:
                    await bot.send_message(target_chat, f"💬 Ответ:\n{msg.text}")
                elif msg.photo:
                    await bot.send_photo(target_chat, msg.photo[-1].file_id, caption=msg.caption or "")
                elif msg.document:
                    await bot.send_document(target_chat, msg.document.file_id, caption=msg.caption or "")
                elif msg.voice:
                    await bot.send_voice(target_chat, msg.voice.file_id)
                elif msg.sticker:
                    await bot.send_sticker(target_chat, msg.sticker.file_id)

                await msg.answer("✅ Ответ отправлен!")
            except Exception as e:
                await msg.answer(f"❌ Не удалось отправить: {e}")
        else:
            await msg.answer("❌ Не могу найти пользователя. Возможно сообщение устарело.")
        return

    # === СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ → ПЕРЕСЫЛАЕМ АДМИНУ ===
    if msg.from_user.id != ADMIN_ID:
        user = msg.from_user
        username = f"@{user.username}" if user.username else "нет username"
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        header = f"📩 Новое сообщение\n👤 {name} ({username})\n🆔 {user.id}\n\n"

        try:
            if msg.text:
                sent = await bot.send_message(ADMIN_ID, header + msg.text)
            elif msg.photo:
                caption = header + (msg.caption or "")
                sent = await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id, caption=caption)
            elif msg.document:
                caption = header + (msg.caption or "")
                sent = await bot.send_document(ADMIN_ID, msg.document.file_id, caption=caption)
            elif msg.voice:
                sent = await bot.send_voice(ADMIN_ID, msg.voice.file_id, caption=header)
            elif msg.sticker:
                await bot.send_message(ADMIN_ID, header + "🎭 Стикер")
                sent = await bot.send_sticker(ADMIN_ID, msg.sticker.file_id)
            else:
                await msg.answer("⚠️ Этот тип сообщений не поддерживается.")
                return

            user_map[sent.message_id] = msg.chat.id
            await msg.answer("✅ Сообщение отправлено! Ожидайте ответа.")

        except Exception as e:
            logging.error(f"Ошибка пересылки: {e}")
            await msg.answer("❌ Произошла ошибка. Попробуйте позже.")


async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
