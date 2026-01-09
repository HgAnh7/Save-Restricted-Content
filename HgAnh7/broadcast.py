from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from database.db import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Thành công"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Đã bị xóa"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Đã chặn Bot"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Lỗi"
    except Exception as e:
        return False, "Lỗi"


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text("**Vui lòng trả lời (reply) lệnh này vào tin nhắn bạn muốn gửi hàng loạt.**")
    
    sts = await message.reply_text(
        text='Đang bắt đầu gửi tin nhắn hàng loạt...'
    )
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

    async for user in users:
        if 'id' in user:
            pti, sh = await broadcast_messages(int(user['id']), b_msg)
            if pti:
                success += 1
            elif pti == False:
                if sh == "Đã chặn Bot":
                    blocked += 1
                elif sh == "Đã bị xóa":
                    deleted += 1
                elif sh == "Lỗi":
                    failed += 1
            done += 1
            
            # Cập nhật trạng thái sau mỗi 20 người dùng để tránh bị giới hạn (FloodWait)
            if not done % 20:
                await sts.edit(f"Đang trong quá trình gửi:\n\nTổng người dùng: {total_users}\nĐã xử lý: {done} / {total_users}\nThành công: {success}\nĐã chặn: {blocked}\nĐã xóa: {deleted}")    
        else:
            # Xử lý trường hợp không tìm thấy 'id' trong dữ liệu người dùng
            done += 1
            failed += 1
            if not done % 20:
                await sts.edit(f"Đang trong quá trình gửi:\n\nTổng người dùng: {total_users}\nĐã xử lý: {done} / {total_users}\nThành công: {success}\nĐã chặn: {blocked}\nĐã xóa: {deleted}")    
    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Gửi tin nhắn hàng loạt hoàn tất:\nThời gian thực hiện: {time_taken}.\n\nTổng người dùng: {total_users}\nĐã xử lý: {done} / {total_users}\nThành công: {success}\nĐã chặn: {blocked}\nĐã xóa: {deleted}")