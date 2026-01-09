import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return 
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Đăng xuất thành công** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**Bạn đã đăng nhập rồi. Vui lòng /logout phiên cũ trước, sau đó mới thực hiện đăng nhập lại.**")
        return 
    user_id = int(message.from_user.id)
    await message.reply("**Cách để tạo Api Id và Api Hash.\n\nLink Video hướng dẫn :- https://youtu.be/LDtgwpI-N7M**")
    api_id_msg = await bot.ask(user_id, "<b>Gửi API ID của bạn.\n\nNhấn vào /skip để bỏ qua bước này\n\nLƯU Ý :- Nếu bạn bỏ qua, tỷ lệ tài khoản bị khóa (ban) sẽ rất cao.</b>", filters=filters.text)
    if api_id_msg.text == "/skip":
        api_id = API_ID
        api_hash = API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("**Api id phải là một số nguyên, hãy bắt đầu lại quá trình bằng lệnh /login**", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
            return
        api_hash_msg = await bot.ask(user_id, "**Bây giờ hãy gửi cho tôi API HASH của bạn**", filters=filters.text)
        api_hash = api_hash_msg.text
        
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>Vui lòng gửi số điện thoại của bạn bao gồm cả mã quốc gia</b>\n<b>Ví dụ:</b> <code>+84123456789, +9171828181889</code>")
    if phone_number_msg.text=='/cancel':
        return await phone_number_msg.reply('<b>Quá trình đã bị hủy !</b>')
    phone_number = phone_number_msg.text
    client = Client(":memory:", api_id, api_hash)
    await client.connect()
    await phone_number_msg.reply("Đang gửi mã OTP...")
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(user_id, "Vui lòng kiểm tra mã OTP trong tài khoản Telegram chính thức. Nếu đã nhận được, hãy gửi OTP vào đây sau khi đọc kỹ định dạng bên dưới. \n\nNếu mã OTP là `12345`, **vui lòng gửi dưới dạng** `1 2 3 4 5`.\n\n**Nhập /cancel để hủy quá trình**", filters=filters.text, timeout=600)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`SỐ ĐIỆN THOẠI` **không hợp lệ.**')
        return
    if phone_code_msg.text=='/cancel':
        return await phone_code_msg.reply('<b>Quá trình đã bị hủy !</b>')
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**Mã OTP không hợp lệ.**')
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**Mã OTP đã hết hạn.**')
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**Tài khoản của bạn đã bật xác minh hai bước. Vui lòng cung cấp mật khẩu.\n\nNhập /cancel để hủy quá trình**', filters=filters.text, timeout=300)
        if two_step_msg.text=='/cancel':
            return await two_step_msg.reply('<b>Quá trình đã bị hủy !</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Mật khẩu cung cấp không chính xác**')
            return
    string_session = await client.export_session_string()
    await client.disconnect()
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Chuỗi phiên (session string) không hợp lệ</b>')
    try:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=api_id, api_hash=api_hash)
            await uclient.connect()
            await db.set_session(message.from_user.id, session=string_session)
            await db.set_api_id(message.from_user.id, api_id=api_id)
            await db.set_api_hash(message.from_user.id, api_hash=api_hash)
            try:
                await uclient.disconnect()
            except:
                pass
    except Exception as e:
        return await message.reply_text(f"<b>LỖI KHI ĐĂNG NHẬP:</b> `{e}`")
    await bot.send_message(message.from_user.id, "<b>Đăng nhập tài khoản thành công.\n\nNếu bạn gặp bất kỳ lỗi nào liên quan đến AUTH KEY, hãy thực hiện /logout trước rồi /login lại.</b>")