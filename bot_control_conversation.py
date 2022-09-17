from pickletools import UP_TO_NEWLINE
from typing import Any, Dict, Tuple
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
import logging

from top_level_conversation import GETTING_BACK

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# State definitions for top level conversation
BOT_CONTROL, WORDLIST, SELECTING_ACTION = map(chr, range(3))
# State definitions for word list conversation
SHOW_LIST, ADD, DELETE = map(chr, range(8,10))
# Meta states
STOPPING, SHOWING = map(chr, range(3, 5))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(
    START_OVER,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(5, 8))

async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    text = f"Please type your long-form word:"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return GET_LONG_WORD

async def get_long_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    text = f"Your long-form word is saved successfully!\nPlease type your short-form word or leave it empty"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return GET_SHORT_WORD

async def get_short_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    text = f"All done, thanks for your time."

    buttons = [
        [
            InlineKeyboardButton('Back', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return GETTING_BACK

async def empty_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    text = f"Your short-form word was leaved empty\nAll Done, Good bye."

    buttons = [
        [
            InlineKeyboardButton('Back', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return GETTING_BACK


add_word_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_word, pattern="^" + str(ADD) + "$")],
    states={
        GET_LONG_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_long_word)],
        GET_SHORT_WORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_short_word),
            CommandHandler("empty", empty_input)
        ],
        GETTING_BACK: [CallbackQueryHandler(return_word_list, pattern="^" + str(BACK) + "$")],
    },
    fallbacks=[
        CommandHandler("stop", stop_nested),
    ],
    map_to_parent={
        # Return to top level menu
        BACK: SELECTING_ACTION,
        # End conversation altogether
        STOPPING: END,
    },
)