import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from data import db

API_TOKEN = "7503710356:AAGbNReWmJIMxcjGo4wfwzwJXyID0Y7ycs8"
ADMIN_ID = 6094902015
CHANNEL = "@morianawitch1"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("📈 Моя статистика"),
         KeyboardButton("🎯 Моя ссылка"))

admin_menu = InlineKeyboardMarkup(row_width=1)
admin_menu.add(
    InlineKeyboardButton("📊 Общая статистика", callback_data="admin_stats"),
    InlineKeyboardButton("🔍 Поиск пользователя", callback_data="search_user"),
    InlineKeyboardButton("♻️ Сбросить статистику", callback_data="reset_stats"),
)

class SearchUserState(StatesGroup):
    waiting_for_query = State()

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    args = message.get_args()
    user = message.from_user
    user_id = user.id

    db.register_user(user_id)
    db.update_user_info(user)

    if args.startswith("ref_"):
        try:
            referrer_id = int(args.replace("ref_", ""))
            if referrer_id != user_id:
                ref_user = db.get_user_by_id(referrer_id)
                ref_name = f"{ref_user[2] or ''} {ref_user[3] or ''}".strip() if ref_user else "пригласителя"
                text = (
                    f"Вы перешли по ссылке от <b>{ref_name}</b>.\n\n"
                    f"Чтобы участие засчиталось — подпишитесь на канал:\n"
                    f"👉 https://t.me/{CHANNEL.lstrip('@')}\n\n"
                    f"После подписки нажмите кнопку ниже 👇"
                )
                kb = InlineKeyboardMarkup()
                kb.add(InlineKeyboardButton("✅ Я подписался", callback_data=f"check_subscribe_{referrer_id}"))
                await message.answer(text, reply_markup=kb)
                return
        except Exception:
            pass

    if user_id != ADMIN_ID:
        member = await bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
        if member.status not in ("member", "creator", "administrator"):
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_direct_subscribe"))
            await message.answer(
                f"🔒 Чтобы продолжить, подпишитесь на канал:\n👉 https://t.me/{CHANNEL.lstrip('@')}",
                reply_markup=kb,
            )
            return

    link = f"https://t.me/Morianaaa_bot?start=ref_{user_id}"
    invite_text = (
        "📌 Вы тоже можете получить расклад — пригласите 3 друга!\n\n"
        f"🔗 Это ваша личная ссылка для приглашения друзей:\n{link}"
    )
    await message.answer(invite_text, reply_markup=menu)

    if user_id == ADMIN_ID:
        await message.answer("🔧 Панель администратора:", reply_markup=admin_menu)

@dp.callback_query_handler(lambda c: c.data == "check_direct_subscribe")
async def check_direct_subscribe(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    member = await bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
    if member.status in ("member", "creator", "administrator"):
        await callback.message.edit_text("✅ Подписка подтверждена!")

        link = f"https://t.me/Morianaaa_bot?start=ref_{user_id}"
        invite_text = (
            "📌 Вы тоже можете получить расклад — пригласите 3 друга!\n\n"
            f"🔗 Это ваша личная ссылка для приглашения друзей:\n{link}"
        )
        await callback.message.answer(invite_text, reply_markup=menu)

        if user_id == ADMIN_ID:
            await callback.message.answer("🔧 Панель администратора:", reply_markup=admin_menu)
    else:
        await callback.message.answer(
            "❗Вы ещё не подписаны на канал. Подпишитесь и нажмите кнопку ещё раз."
        )

@dp.callback_query_handler(lambda c: c.data.startswith("check_subscribe_"))
async def check_subscribe(callback: types.CallbackQuery):
    referred_by = int(callback.data.replace("check_subscribe_", ""))
    user_id = callback.from_user.id
    member = await bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)

    if member.status in ("member", "creator", "administrator"):
        db.add_referral(referred_by, user_id)
        await callback.message.edit_text("✅ Подписка подтверждена! Вы засчитаны как приглашённый.")

        link = f"https://t.me/Morianaaa_bot?start=ref_{user_id}"
        invite_text = (
            "📌 Вы тоже можете получить расклад — пригласите 3 друга!\n\n"
            f"🔗 Это ваша личная ссылка для приглашения друзей:\n{link}"
        )
        await callback.message.answer(invite_text, reply_markup=menu)
    else:
        await callback.message.answer(
            "❗Вы ещё не подписаны на канал. Подпишитесь и нажмите кнопку ещё раз."
        )

@dp.message_handler(lambda m: m.text == "📈 Моя статистика")
async def my_stats(message: types.Message):
    user_id = message.from_user.id
    cnt = db.get_referral_count(user_id)
    link = f"https://t.me/Morianaaa_bot?start=ref_{user_id}"
    await message.answer(
        f"Вы пригласили: <b>{cnt}</b> человек(а)\n\n"
        f"🔗 Это ваша личная ссылка для приглашения друзей:\n{link}"
    )

@dp.message_handler(lambda m: m.text == "🎯 Моя ссылка")
async def my_link(message: types.Message):
    link = f"https://t.me/Morianaaa_bot?start=ref_{message.from_user.id}"
    await message.answer(f"🔗 Это ваша личная ссылка для приглашения друзей:\n{link}")

@dp.callback_query_handler(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    users = db.get_all_users()
    data = []
    for user in users:
        user_id = user[1]
        username = user[2]
        first_name = user[3]
        name = f"@{username}" if username else (first_name or str(user_id))
        count = db.get_referral_count(user_id)
        data.append((name, count))

    if not data:
        await callback.message.answer("❗Нет зарегистрированных пользователей.")
        return

    data.sort(key=lambda x: x[1], reverse=True)
    msg = "<b>📊 Топ по приглашениям:</b>\n\n"
    for i, (name, count) in enumerate(data[:20], start=1):
        msg += f"{i}. {name}: {count} приглашений\n"

    await callback.message.answer(msg)

@dp.callback_query_handler(lambda c: c.data == "search_user")
async def search_user_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 Введите username, имя или ID:")
    await state.set_state(SearchUserState.waiting_for_query)

@dp.message_handler(state=SearchUserState.waiting_for_query)
async def search_user_process(message: types.Message, state: FSMContext):
    query = message.text.lower()
    users = db.get_all_users()
    found = None
    for user in users:
        user_id = user[1]
        username = (user[2] or "").lower()
        first_name = (user[3] or "").lower()
        if query in username or query in first_name or query in str(user_id):
            count = db.get_referral_count(user_id)
            name = user[2] or user[3] or str(user_id)
            found = f"👤 {name}\n📨 Приглашено: {count}\nID: {user_id}"
            break

    if found:
        await message.answer(found)
    else:
        await message.answer("❌ Пользователь не найден.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "reset_stats")
async def reset_stats(callback: types.CallbackQuery):
    db.reset_referrals()
    await callback.message.answer("♻️ Статистика сброшена.")

if __name__ == "__main__":
    db.init_db()
    executor.start_polling(dp, skip_updates=True)