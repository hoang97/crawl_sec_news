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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# State definitions for top level conversation
BOT_CONTROL, WORDLIST, SELECTING_ACTION = map(chr, range(3))
# State definitions for bot control conversation
START_BOT, STOP_BOT = map(chr, range(3, 5))
# State definitions for word list conversation
SHOW_LIST, ADD, DELETE = map(chr, range(5, 8))
# Meta states
STOPPING, SHOWING, GETTING_BACK, BACK = map(chr, range(8, 12))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(
    START_OVER,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(12, 15))

# Top level conversation callbacks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""
    text = (
        "You may choose to add a family member, yourself, show the gathered data, or end the "
        "conversation. To abort, simply type /stop."
    )

    buttons = [
        [
            InlineKeyboardButton(text="Bot actions", callback_data=str(BOT_CONTROL)),
        ],
        [
            InlineKeyboardButton(text="Word list", callback_data=str(WORDLIST)),
        ],
        [
            InlineKeyboardButton(text="Done", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(
            "Hi, I'm Family Bot and I'm here to help you gather information about your family."
        )
        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return SELECTING_ACTION


async def bot_control(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Pretty print gathered data."""

    user_data = context.user_data
    text = f"bot_control:"

    buttons = [
        [
            InlineKeyboardButton('Start bot', callback_data=str(START_BOT)), 
            InlineKeyboardButton('Stop bot', callback_data=str(STOP_BOT)),
        ], 
        [
            InlineKeyboardButton('Main menu', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SELECTING_ACTION


async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Pretty print gathered data."""

    user_data = context.user_data
    text = f"bot is starting ..."

    buttons = [[InlineKeyboardButton(text="Back", callback_data=str(BACK))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return GETTING_BACK


async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Pretty print gathered data."""

    user_data = context.user_data
    text = f"bot is stoping ..."

    buttons = [[InlineKeyboardButton(text="Back", callback_data=str(BACK))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return GETTING_BACK
    

async def return_bot_control(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await bot_control(update, context)

    return SELECTING_ACTION


async def return_top_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END

    
async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Completely end conversation from within nested conversation."""
    await update.message.reply_text("Okay, bye.")

    return STOPPING


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye.")

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    await update.callback_query.answer()

    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)

    return END


async def word_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Add information about yourself."""
    user_data = context.user_data
    text = f"word list command board:"

    buttons = [
        [
            InlineKeyboardButton('Show', callback_data=str(SHOW_LIST)), 
            InlineKeyboardButton('Add', callback_data=str(ADD)),
            InlineKeyboardButton('Delete', callback_data=str(DELETE)),
        ], 
        [
            InlineKeyboardButton('Main menu', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SELECTING_ACTION

async def show_word_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    text = f"word list:"

    buttons = [
        [
            InlineKeyboardButton('Back', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return GETTING_BACK

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

async def delete_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    text = f"add word:"
    buttons = [
        [
            InlineKeyboardButton('Back', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return GETTING_BACK


async def return_word_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await word_list(update, context)

    return SELECTING_ACTION


wordlist_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(word_list, pattern="^" + str(WORDLIST) + "$")],
    states={
        SHOWING: [CallbackQueryHandler(word_list, pattern="^" + str(WORDLIST) + "$")],
        SELECTING_ACTION: [
            CallbackQueryHandler(show_word_list, pattern="^" + str(SHOW_LIST) + "$"),
            CallbackQueryHandler(add_word, pattern="^" + str(ADD) + "$"),
            CallbackQueryHandler(delete_word, pattern="^" + str(DELETE) + "$"),
        ],
        GETTING_BACK: [CallbackQueryHandler(return_word_list, pattern="^" + str(BACK) + "$")],
    },
    fallbacks=[
        CallbackQueryHandler(return_top_level, pattern="^" + str(END) + "$"),
        CommandHandler("stop", stop_nested),
    ],
    map_to_parent={
        # Return to top level menu
        END: SELECTING_ACTION,
        # End conversation altogether
        STOPPING: END,
    },
)

bot_control_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(bot_control, pattern="^" + str(BOT_CONTROL) + "$")],
    states={
        SHOWING: [CallbackQueryHandler(bot_control, pattern="^" + str(BOT_CONTROL) + "$")],
        SELECTING_ACTION: [
            CallbackQueryHandler(start_bot, pattern="^" + str(START_BOT) + "$"), 
            CallbackQueryHandler(stop_bot, pattern="^" + str(STOP_BOT) + "$"),
        ],
        GETTING_BACK: [CallbackQueryHandler(return_bot_control, pattern="^" + str(BACK) + "$")],
    },
    fallbacks=[
        CallbackQueryHandler(return_top_level, pattern="^" + str(END) + "$"),
        CommandHandler("stop", stop_nested),
    ],
    map_to_parent={
        # Return to top level menu
        END: SELECTING_ACTION,
        # End conversation altogether
        STOPPING: END,
    },
)

# Set up top level ConversationHandler (selecting action)
# Because the states of the third level conversation map to the ones of the second level
# conversation, we need to make sure the top level conversation can also handle them
selection_handlers = [
    bot_control_conv,
    wordlist_conv,
    CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
]

top_level_conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SHOWING: [CallbackQueryHandler(start, pattern="^" + str(END) + "$")],
        SELECTING_ACTION: selection_handlers,
        STOPPING: [CommandHandler("start", start)],
    },
    fallbacks=[CommandHandler("stop", stop)],
)


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5538324444:AAF3O9TbuWophnrxNRfg93xvVNsd7PuBIus").build()

    application.add_handler(top_level_conv)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()