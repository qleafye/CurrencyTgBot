from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from admin_handlers import AdminHandlers
from database import Database
from handlers import MessageHandlers
from bestchange_api import BestChange

class CurrencyBot:
    def __init__(self, token: str):
        self.token = token
        self.api_handler = BestChange()
        self.app = Application.builder().token(self.token).build()
        
        # Инициализация компонентов
        self.db = Database('users_db.json', 'user_logs.json', 'admin_config.json')
        self.admin_handlers = AdminHandlers(self)
        self.message_handlers = MessageHandlers(self)
        
        # Загружаем админов
        self.ADMIN_IDS = self.db.load_admin_ids()
        
        # Регистрируем обработчики
        self._register_handlers()

    def _register_handlers(self):
        # Админские команды
        self.app.add_handler(CommandHandler("stats", self.admin_handlers.stats))
        self.app.add_handler(CommandHandler("broadcast", self.admin_handlers.broadcast))
        self.app.add_handler(CommandHandler("addadmin", self.admin_handlers.add_admin))
        self.app.add_handler(CommandHandler("removeadmin", self.admin_handlers.remove_admin))
        self.app.add_handler(CommandHandler("listadmins", self.admin_handlers.list_admins))
        
        # Основные команды
        self.app.add_handler(CommandHandler("start", self.message_handlers.start))
        self.app.add_handler(CommandHandler("help", self.message_handlers.help_command))
        self.app.add_handler(CallbackQueryHandler(self.message_handlers.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handlers.receive_price))

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self.ADMIN_IDS

    def run(self):
        print("Бот запущен...")
        self.app.run_polling()