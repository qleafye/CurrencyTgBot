from bestchange_api import BestChange
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

class BestChangeAPI:
    def __init__(self):
        self.api = BestChange()

    def get_min_rate(self, give_id, get_id):
        rates = self.api.rates().get()
        rates_list = [rate['rate'] for rate in rates if rate['give_id'] == give_id and rate['get_id'] == get_id]
        return min(rates_list) if rates_list else None

class CurrencyBot:
    def __init__(self, token: str):
        self.token = token
        self.api_handler = BestChangeAPI()
        self.app = Application.builder().token(self.token).build()

        # Регистрируем обработчики
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_price))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("CNY ¥", callback_data="105_165")],
            [InlineKeyboardButton("USD $", callback_data="105_58")],
            [InlineKeyboardButton("JPY ¥", callback_data="105_232")],
            [InlineKeyboardButton("EUR €", callback_data="105_65")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Привет! Я SYTNXXbot, я помогу тебе сориентироваться в цене твоего заказа.\n"
                                        "Выберите валюту, которая указана на сайте товара:", reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # Подтверждение нажатия кнопки

        # Разбиваем callback_data на give_id и get_id
        callback_data = query.data
        give_id, get_id = map(int, callback_data.split("_"))

        # Ищем минимальный курс
        min_rate = self.api_handler.get_min_rate(give_id, get_id)

        # Ответ пользователю
        if min_rate is not None:
            response = "Теперь, отправьте цену, которую вы хотите обменять."
            # Сохраняем give_id и get_id для дальнейшего использования
            context.user_data['give_id'] = give_id
            context.user_data['get_id'] = get_id
            context.user_data['min_rate'] = min_rate
        else:
            response = "К сожалению, все обменники закрыты."

        await query.edit_message_text(text=response)

    async def receive_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Получаем цену от пользователя
            price = float(update.message.text)

            # Извлекаем минимальный курс из данных пользователя
            min_rate = context.user_data.get('min_rate')

            if min_rate:
                # Рассчитываем стоимость
                result = price * min_rate
                response = f"Цена за ваш товар: {result * 1.15:.2f}"

                response += ("\nДля заказа пишите @sytnixxstore")

                response += ("\nТеперь выберите валюту снова.")

                # Очистим данные пользователя, чтобы начать новый процесс
                context.user_data.clear()

                # Отправляем пользователю сообщение с кнопками
                keyboard = [
                    [InlineKeyboardButton("CNY ¥", callback_data="105_165")],
                    [InlineKeyboardButton("USD $", callback_data="105_58")],
                    [InlineKeyboardButton("JPY ¥", callback_data="105_232")],
                    [InlineKeyboardButton("EUR €", callback_data="105_65")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(response, reply_markup=reply_markup)

            else:
                response = "Не был выбран курс. Пожалуйста, выберите валюту снова."

        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное число.")

    def run(self):
        # Запуск бота
        print("Бот запущен...")
        self.app.run_polling()