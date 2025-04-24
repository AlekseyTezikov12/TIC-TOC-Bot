import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from game import empty_board, ai_move, check_winner

logging.basicConfig(level=logging.INFO)
games = {}

def build_keyboard(board):
    keyboard = []
    for i in range(0, 9, 3):
        row = [
            InlineKeyboardButton(text=cell if cell != ' ' else str(i + j + 1), callback_data=f"move:{i + j}")
            for j, cell in enumerate(board[i:i+3])
        ]
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    games[user_id] = {
        "board": empty_board(),
        "current": "X"
    }
    await update.message.reply_text("Ты играешь против умного ИИ! Твой ход:", reply_markup=build_keyboard(games[user_id]["board"]))

async def handle_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = games.get(user_id)

    if not data:
        await query.answer("Игра не найдена. Нажми /start.", show_alert=True)
        return

    index = int(query.data.split(":")[1])
    board = data["board"]

    if board[index] != ' ':
        await query.answer("Эта клетка занята!")
        return

    board[index] = "X"
    if check_winner(board) == "X":
        await query.edit_message_text("Ты победил!", reply_markup=build_keyboard(board))
        games.pop(user_id)
        return

    if ' ' not in board:
        await query.edit_message_text("Ничья!", reply_markup=build_keyboard(board))
        games.pop(user_id)
        return

    ai_index = ai_move(board)
    board[ai_index] = "O"
    if check_winner(board) == "O":
        await query.edit_message_text("ИИ победил!", reply_markup=build_keyboard(board))
        games.pop(user_id)
        return

    if ' ' not in board:
        await query.edit_message_text("Ничья!", reply_markup=build_keyboard(board))
        games.pop(user_id)
        return

    await query.edit_message_reply_markup(reply_markup=build_keyboard(board))

if __name__ == "__main__":
    app = ApplicationBuilder().token("7902498490:AAHfvz-5YAMF2k5KuTNCH8_B1UDbfLA-cz8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_move, pattern="^move:"))
    app.run_polling()