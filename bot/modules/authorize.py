from bot import AUTHORIZED_CHATS, SUDO_USERS, dispatcher, DB_URI
from bot.helper.telegram_helper.message_utils import sendMessage
from telegram.ext import CommandHandler
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.db_handler import DbManger


def authorize(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            msg = '𝗨𝘀𝗲𝗿 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱!!🤦‍♂️'
        elif DB_URI is not None:
            msg = DbManger().user_auth(user_id)
            AUTHORIZED_CHATS.add(user_id)
        else:
            AUTHORIZED_CHATS.add(user_id)
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = '𝗨𝘀𝗲𝗿 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱✅'
    elif reply_message is None:
        # Trying to authorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            msg = '𝗖𝗵𝗮𝘁 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱!!🤦‍♂️'
        elif DB_URI is not None:
            msg = DbManger().user_auth(chat_id)
            AUTHORIZED_CHATS.add(chat_id)
        else:
            AUTHORIZED_CHATS.add(chat_id)
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{chat_id}\n')
                msg = '𝗖𝗵𝗮𝘁 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱✅'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            msg = '𝗨𝘀𝗲𝗿 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱!!🤦‍♂️'
        elif DB_URI is not None:
            msg = DbManger().user_auth(user_id)
            AUTHORIZED_CHATS.add(user_id)
        else:
            AUTHORIZED_CHATS.add(user_id)
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = '𝗨𝘀𝗲𝗿 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱✅'
    sendMessage(msg, context.bot, update)

def unauthorize(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(user_id)
            else:
                msg = '𝗨𝘀𝗲𝗿 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱✅'
            AUTHORIZED_CHATS.remove(user_id)
        else:
            msg = '𝗨𝘀𝗲𝗿 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱!!🤦‍♂️'
    elif reply_message is None:
        # Trying to unauthorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(chat_id)
            else:
                msg = '𝗖𝗵𝗮𝘁 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱✅'
            AUTHORIZED_CHATS.remove(chat_id)
        else:
            msg = '𝗖𝗵𝗮𝘁 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱!!🤦‍♂️'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(user_id)
            else:
                msg = '𝗨𝘀𝗲𝗿 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 ✅'
            AUTHORIZED_CHATS.remove(user_id)
        else:
            msg = '𝗨𝘀𝗲𝗿 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱!!🤦‍♂️'
    if DB_URI is None:
        with open('authorized_chats.txt', 'a') as file:
            file.truncate(0)
            for i in AUTHORIZED_CHATS:
                file.write(f'{i}\n')
    sendMessage(msg, context.bot, update)

def addSudo(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            msg = '𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗜𝗻 𝗦𝘂𝗱𝗼 𝗠𝗲𝗺𝗯𝗲𝗿!!🤦‍♂️'
        elif DB_URI is not None:
            msg = DbManger().user_addsudo(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            with open('sudo_users.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = '𝗣𝗿𝗼𝗺𝗼𝘁𝗲𝗱 𝗔𝘀 𝗦𝘂𝗱𝗼✅'
    elif reply_message is None:
        msg = "Give ID or Reply To message of whom you want to Promote."
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            msg = '𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗶𝗻 𝗦𝘂𝗱𝗼 𝗺𝗲𝗺𝗯𝗲𝗿🤦‍♂️'
        elif DB_URI is not None:
            msg = DbManger().user_addsudo(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            with open('sudo_users.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = '𝗣𝗿𝗼𝗺𝗼𝘁𝗲𝗱 𝗔𝘀 𝘀𝘂𝗱𝗼✅'
    sendMessage(msg, context.bot, update)

def removeSudo(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().user_rmsudo(user_id)
            else:
                msg = '𝗗𝗲𝗺𝗼𝘁𝗲𝗱 𝗵𝗮𝘀 𝘀𝘂𝗱𝗼 𝗠𝗲𝗺𝗯𝗲𝗿✅'
            SUDO_USERS.remove(user_id)
        else:
            msg = '𝗡𝗼𝘁 𝘀𝘂𝗱𝗼 𝘂𝘀𝗲𝗿 𝘁𝗼 𝗱𝗲𝗺𝗼𝘁𝗲!!🤦‍♂️'
    elif reply_message is None:
        msg = "Give ID or Reply To message of whom you want to remove from Sudo"
    else:
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().user_rmsudo(user_id)
            else:
                msg = '𝗗𝗲𝗺𝗼𝘁𝗲𝗱 𝗵𝗮𝘀 𝗦𝘂𝗱𝗼 𝗠𝗲𝗺𝗯𝗲𝗿✅'
            SUDO_USERS.remove(user_id)
        else:
            msg = '𝗡𝗼𝘁 𝗦𝘂𝗱𝗼 𝘂𝘀𝗲𝗿 𝘁𝗼 𝗱𝗲𝗺𝗼𝘁𝗲!!🤦‍♂️'
    if DB_URI is None:
        with open('sudo_users.txt', 'a') as file:
            file.truncate(0)
            for i in SUDO_USERS:
                file.write(f'{i}\n')
    sendMessage(msg, context.bot, update)

def sendAuthChats(update, context):
    user = sudo = ''
    user += '\n'.join(f"<code>{uid}</code>" for uid in AUTHORIZED_CHATS)
    sudo += '\n'.join(f"<code>{uid}</code>" for uid in SUDO_USERS)
    sendMessage(f'<b><u>Authorized Chats:</u></b>\n{user}\n<b><u>Sudo Users:</u></b>\n{sudo}', context.bot, update)


send_auth_handler = CommandHandler(command=BotCommands.AuthorizedUsersCommand, callback=sendAuthChats,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
authorize_handler = CommandHandler(command=BotCommands.AuthorizeCommand, callback=authorize,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
unauthorize_handler = CommandHandler(command=BotCommands.UnAuthorizeCommand, callback=unauthorize,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
addsudo_handler = CommandHandler(command=BotCommands.AddSudoCommand, callback=addSudo,
                                    filters=CustomFilters.owner_filter, run_async=True)
removesudo_handler = CommandHandler(command=BotCommands.RmSudoCommand, callback=removeSudo,
                                    filters=CustomFilters.owner_filter, run_async=True)

dispatcher.add_handler(send_auth_handler)
dispatcher.add_handler(authorize_handler)
dispatcher.add_handler(unauthorize_handler)
dispatcher.add_handler(addsudo_handler)
dispatcher.add_handler(removesudo_handler)
