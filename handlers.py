from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

class MessageHandlers:
    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.bot.db.save_user(update.message.from_user)
        self.bot.db.log_operation(
            update.message.from_user.id,
            'start',
            'Пользователь запустил бота'
        )
        
        keyboard = [
            [InlineKeyboardButton("🇨🇳 CNY (Юань)", callback_data="105_165")],
            [InlineKeyboardButton("🇺🇸 USD (Доллар)", callback_data="105_58")],
            [InlineKeyboardButton("🇪🇺 EUR (Евро)", callback_data="105_65")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_message = (
            "👋 *Добро пожаловать!*\n\n"
            "Я помогу рассчитать стоимость вашего заказа в рублях.\n\n"
            "🔸 *Как пользоваться:*\n"
            "1. Выберите валюту товара\n"
            "2. Введите сумму\n"
            "3. Получите результат\n\n"
            "📊 *Выберите валюту товара:*"
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        base_help = (
            "🔍 *Основные команды:*\n\n"
            "/start - Запустить бота\n"
            "/help - Показать это сообщение\n"
            "💡 Для расчета стоимости просто выберите валюту и введите сумму!"
        )

        # Если пользователь админ, добавляем список админских команд
        if self.bot._is_admin(update.effective_user.id):
            admin_help = (
                "\n\n👑 *Команды администратора:*\n\n"
                "/stats - Статистика использования бота\n"
                "/broadcast - Отправить сообщение всем пользователям\n"
                "/addadmin - Добавить нового администратора\n"
                "/removeadmin - Удалить администратора\n"
                "/listadmins - Показать список администраторов"
            )
            help_text = base_help + admin_help
        else:
            help_text = base_help

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        # Логируем выбор валюты
        self.bot.db.log_operation(
            query.from_user.id,
            'currency_selection',
            f'Выбрана валюта: {query.data}'
        )
        
        callback_data = query.data
        give_id, get_id = map(int, callback_data.split("_"))
        min_rate = self.bot.api_handler.get_min_rate(give_id, get_id)

        if min_rate is not None:
            response = "💰 *Введите сумму для расчета:*"
            context.user_data['give_id'] = give_id
            context.user_data['get_id'] = get_id
            context.user_data['min_rate'] = min_rate
        else:
            response = "⚠️ К сожалению, сервис временно недоступен."

        await query.edit_message_text(text=response, parse_mode='Markdown')

    async def receive_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            price = float(update.message.text)
            min_rate = context.user_data.get('min_rate')

            if min_rate:
                result = price * min_rate
                
                # Логируем расчет
                self.bot.db.log_operation(
                    update.message.from_user.id,
                    'calculation',
                    {
                        'input_amount': price,
                        'rate': min_rate,
                        'result': result + 1700
                    }
                )
                
                response = (
                    "🔢 *Результат расчета:*\n\n"
                    f"💵 Стоимость: `{result + 1700:.2f}` RUB\n\n"
                    "📱 Для заказа: @sytnixxstore\n\n"
                    "🔄 Выберите валюту для нового расчета:"
                )

                keyboard = [
                    [InlineKeyboardButton("🇨🇳 CNY (Юань)", callback_data="105_165")],
                    [InlineKeyboardButton("🇺🇸 USD (Доллар)", callback_data="105_58")],
                    [InlineKeyboardButton("🇪🇺 EUR (Евро)", callback_data="105_65")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.message.reply_text("⚠️ Пожалуйста, сначала выберите валюту.")
        except ValueError:
            await update.message.reply_text("⚠️ Пожалуйста, введите корректное число.")

    # ... остальные обработчики сообщений ... 