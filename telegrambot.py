#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Application class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import logging
import subprocess
import re

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables
DEVELOPER_ID = 1542646167
START_OVER = 'START_OVER'
WORDLIST_OVER = 'WORDLIST_OVER'
# Stages
LAYER1_ROUTES, LAYER2_ROUTES, END_ROUTES = range(3)
# Callback data
BACK, EXIT = range(2)
# layer 1
BOT_ACTION, WORD_LIST = range(2,4)
# layer 2
START, STOP = range(4,6)
ADD, DELETE, SHOW = range(6,9)
# layer 3
SAVE_LONG_WORD, SAVE_SHORT_WORD, DELETE_WORD = range(9,12)
# END
END = ConversationHandler.END


def extract_total_request(log):
    '''Get total request count from scrapy log'''
    request_extractor = re.compile(r"(?<=downloader\/request_count': )(?P<request_count>\d+)", flags=re.MULTILINE)
    request_count = request_extractor.search(log).group('request_count')
    return int(request_count)

def extract_response_code(log):
    '''Get all http code and count from scrapy log'''
    response_code_extractor = re.compile(r"(?<=downloader\/response_status_count\/)(?P<response_code>\d+)': (?P<count>\d+)", flags=re.MULTILINE)
    matches = response_code_extractor.finditer(log)
    for match in matches:
        yield {
            'response_code': int(match.group('response_code')),
            'count': int(match.group('count'))
        }

def is_blocked(log):
    '''
    - Return empty string if bot is ok
    - Return WARNING message if bot is blocked
    '''
    total_request = extract_total_request(log)
    msg = f'CẢNH BÁO BLOCK!!!\nTổng số request: {total_request}'
    total_success = 0

    for data in extract_response_code(log):
        response_code = data['response_code']
        count = data['count']
        msg += f'\nSố lượng response code {response_code}: {count}'
        if response_code == 200:
            total_success += count

    if total_success < total_success/2:
        return msg
    return ''

def run_subprocess(command, context):
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = process.stderr.decode('utf-8')
    msg = is_blocked(stderr)
    if msg:
        context.bot.send_message(DEVELOPER_ID, text=msg)
    print(stderr)

async def crawl(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Run subprocess to scrapy
    """
    job = context.job
    chat_id = job.chat_id
    print(chat_id)

    command_crawl_itsec = f'scrapy crawl itsecguru -a chat_id={chat_id}'
    
    run_subprocess(command_crawl_itsec, context)

# async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send the alarm message."""
#     job = context.job
#     await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""

    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Bot Action", callback_data=str(BOT_ACTION)),
            InlineKeyboardButton("Word List", callback_data=str(WORD_LIST)),
            InlineKeyboardButton("Exit", callback_data=str(EXIT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Welcome to our bot"

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text + " (new)", reply_markup=reply_markup)

    context.user_data[START_OVER] = False
    context.user_data[WORDLIST_OVER] = True

    # Tell ConversationHandler that we're in state `FIRST` now
    return LAYER1_ROUTES

async def start_new_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[START_OVER] = False
    await start(update, context)

    return LAYER1_ROUTES


async def btn_botAction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Start Crawl", callback_data=str(START)),
            InlineKeyboardButton("Stop Crawl", callback_data=str(STOP)),
            InlineKeyboardButton("Back", callback_data=str(BACK)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Please choose an action for our bot", reply_markup=reply_markup
    )
    context.user_data[START_OVER] = True
    return LAYER2_ROUTES


async def btn_wordList_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    keyboard = [
        [
            InlineKeyboardButton("Add", callback_data=str(ADD)),
            InlineKeyboardButton("Delete", callback_data=str(DELETE)),
            InlineKeyboardButton("Show", callback_data=str(SHOW)),
            InlineKeyboardButton("Back", callback_data=str(BACK)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Please choose an action for our wordlist"
    # If we're starting over we don't need to send a new message
    if context.user_data.get(WORDLIST_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text + " (new)", reply_markup=reply_markup)

    context.user_data[WORDLIST_OVER] = False

    context.user_data[START_OVER] = True
    return LAYER2_ROUTES


async def btn_startCrawl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""

    chat_id = update.effective_message.chat_id
    text = "Error"

    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(crawl, 2, chat_id=chat_id, name=str(chat_id), data=2)

        text = "Crawling bot started successfully!!"
        if job_removed:
            text += "Crawling bot restarted!!"

    except (IndexError, ValueError):
        pass

    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(BOT_ACTION)),
            InlineKeyboardButton("Exit", callback_data=str(EXIT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    context.user_data[START_OVER] = True
    return LAYER1_ROUTES


async def btn_stopCrawl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""

    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Crawling bot stoped successfully!!" if job_removed else "Crawling bot not start yet."

    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(BOT_ACTION)),
            InlineKeyboardButton("Exit", callback_data=str(EXIT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    context.user_data[START_OVER] = True
    return LAYER1_ROUTES


async def btn_showWordList_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(WORD_LIST)),
            InlineKeyboardButton("Exit", callback_data=str(EXIT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="This is our list: ... nothing haha", reply_markup=reply_markup
    )
    context.user_data[WORDLIST_OVER] = True
    return LAYER1_ROUTES


async def btn_addWord_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Please input your long-form word")

    return SAVE_LONG_WORD
    
async def btn_deleteWord_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Type your word that you want to delete from word list")
    
    context.user_data[WORDLIST_OVER] = True

    return DELETE_WORD

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    context.user_data[START_OVER] = False
    return END

async def save_long_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Save input for feature and return to feature selection."""
    user_data = context.user_data
    user_data['long'] = update.message.text

    await update.message.reply_text(text=f"Your long-form word is: {user_data['long']}.\nPlease input your short-form word")

    return SAVE_SHORT_WORD

async def save_short_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Save input for feature and return to feature selection."""
    user_data = context.user_data
    user_data['short'] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(WORD_LIST)),
            InlineKeyboardButton("Exit", callback_data=str(EXIT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=f"Your short-form word is: {user_data['short']}. All Done!!!", reply_markup=reply_markup)
    
    context.user_data[WORDLIST_OVER] = True

    return LAYER1_ROUTES

async def cancel_add_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[WORDLIST_OVER] = False
    await btn_wordList_handler(update, context)

    return END

async def delete_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Save input for feature and return to feature selection."""
    user_data = context.user_data
    user_data['delete'] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(WORD_LIST)),
            InlineKeyboardButton("Exit", callback_data=str(EXIT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=f"Deleted word : {user_data['delete']}. All Done!!!", reply_markup=reply_markup)
    
    context.user_data[WORDLIST_OVER] = True

    return LAYER1_ROUTES

async def cancel_delete_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[WORDLIST_OVER] = False
    await btn_wordList_handler(update, context)

    return END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5538324444:AAF3O9TbuWophnrxNRfg93xvVNsd7PuBIus").build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'

    addWord_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(btn_addWord_handler, pattern="^" + str(ADD) + "$")],
        states={
            SAVE_LONG_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_long_word)],
            SAVE_SHORT_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_short_word)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_add_conv, pattern="^" + str(BACK) + "$"),
            CommandHandler("cancel", cancel_add_conv),
        ],
        map_to_parent={
            LAYER1_ROUTES: LAYER1_ROUTES,
            # after end add conversation -> return to layer1_routes
            END: LAYER2_ROUTES,
            # after exit -> end menu altogether
            EXIT: END
        }
    )

    deleteWord_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(btn_deleteWord_handler, pattern="^" + str(DELETE) + "$")],
        states={
            DELETE_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_word)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_delete_conv),
        ],
        map_to_parent={
            LAYER1_ROUTES: LAYER1_ROUTES,
            # after end add conversation -> return to layer1_routes
            END: LAYER2_ROUTES,
            # after exit -> end menu altogether
            EXIT: END
        }
    )

    menu_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LAYER1_ROUTES: [
                CallbackQueryHandler(btn_botAction_handler, pattern="^" + str(BOT_ACTION) + "$"),
                CallbackQueryHandler(btn_wordList_handler, pattern="^" + str(WORD_LIST) + "$"),
            ],
            LAYER2_ROUTES: [
                CallbackQueryHandler(btn_startCrawl_handler, pattern="^" + str(START) + "$"),
                CallbackQueryHandler(btn_stopCrawl_handler, pattern="^" + str(STOP) + "$"),
                addWord_handler,
                deleteWord_handler,
                CallbackQueryHandler(btn_showWordList_handler, pattern="^" + str(SHOW) + "$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(start, pattern="^" + str(BACK) + "$"),
            CallbackQueryHandler(end, pattern="^" + str(EXIT) + "$"),
            CommandHandler("start", start_new_one),
        ],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(menu_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()