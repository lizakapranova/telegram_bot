from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging

users = {}

token = '5880378961:AAGbIL672-gIg9jKsMQ-pKC2UycZ9DaZwd0'
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)


class Statements(StatesGroup):
    admins = State()
    ban = State()
    unban = State()


async def update(message):
    if message.chat.id in users.keys():
        for member in message.new_chat_members:
            users[message.chat.id]['@' + member.username] = member.id
    else:
        users[message.chat.id] = {}
        for member in message.new_chat_members:
            users[message.chat.id]['@' + member.username] = member.id


async def admin_check(message):
    for admin in (await bot.get_chat_administrators(chat_id=message.chat.id)):
        if admin['user']['id'] == message.from_user.id:
            return True
    return False


@dp.message_handler(commands=['start'])
async def start(message):
    if await admin_check(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        menu = [types.KeyboardButton("Add admin"),
                types.KeyboardButton("Ban user"),
                types.KeyboardButton("Ban all"),
                types.KeyboardButton("Unban user"),
                types.KeyboardButton("Make invite link")]

        for but in menu:
            markup.add(but)

        await message.answer(text="Hello!", reply_markup=markup)


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def reply(message):
    await message.answer(text='Hello')
    await update(message)


@dp.message_handler(content_types='text', text='Add admin')
async def add_admin(message):
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Enter username:'
        await message.answer(text=output, reply_markup=keyboard)
        await Statements.admins.set()


@dp.message_handler(state=Statements.admins)
async def make_admin(message, state):
    print(users)
    try:
        user_id = int(users[message.chat.id][message.text.strip(' ')])
        print(1)
        await bot.promote_chat_member(chat_id=message.chat.id, user_id=user_id,
                                      can_manage_chat=True,
                                      can_change_info=True,
                                      can_delete_messages=True,
                                      can_manage_video_chats=True,
                                      can_promote_members=True,
                                      can_pin_messages=True,
                                      can_edit_messages=True,
                                      can_post_messages=True,
                                      can_restrict_members=True,
                                      can_invite_users=True)
        print(2)
        await message.answer('Admin has been added')
    except KeyError:
        await message.reply('Unknown user')
    await state.finish()


@dp.message_handler(content_types='text', text='Ban user')
async def ban(message):
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Enter username:'
        await message.answer(text=output, reply_markup=keyboard)
        await Statements.ban.set()


@dp.message_handler(state=Statements.ban)
async def blacklist(message, state):
    try:
        user_id = int(users[message.chat.id][message.text.strip(' ')])
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.answer('User has been banned')
    except KeyError:
        await message.reply('Unknown user')
    await state.finish()


@dp.message_handler(content_types='text', text='Ban all')
async def ban_all(message):
    print(users)
    if await admin_check(message):
        for user in users[message.chat.id]:
            print(user)
            user_id = int(users[message.chat.id][user])
            await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.reply('All users have been banned')


@dp.message_handler(content_types='text', text='Unban user')
async def ban(message):
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Enter username:'
        await message.answer(text=output, reply_markup=keyboard)
        await Statements.unban.set()


@dp.message_handler(state=Statements.unban)
async def blacklist(message, state):
    try:
        user_id = int(users[message.chat.id][message.text.strip(' ')])
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.answer('User has been unbanned')
    except KeyError:
        await message.reply('Unknown user')
    await state.finish()


@dp.message_handler(content_types='text', text='Make invite link')
async def link(message):
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        invite = await bot.create_chat_invite_link(message.chat.id)
        output = invite.invite_link
        await message.answer(text=output, reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
