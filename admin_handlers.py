from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import json

class AdminHandlers:
    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.bot._is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ У вас нет прав для использования этой команды.")
            return
        
        try:
            logs = self.bot.db.get_logs()
            users = self.bot.db.get_users()
            
            today = datetime.now().date()
            today_logs = [log for log in logs if datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S').date() == today]
            
            stats = (
                "📊 *Статистика бота:*\n\n"
                f"👥 Всего пользователей: {len(users)}\n"
                f"📈 Всего операций: {len(logs)}\n"
                f"🔄 Операций сегодня: {len(today_logs)}\n"
                f"✨ Активных сегодня: {len(set(log['user_id'] for log in today_logs))}"
            )
            await update.message.reply_text(stats, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при получении статистики: {str(e)}")

    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.bot._is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ У вас нет прав для использования этой команды.")
            return
            
        if not context.args:
            await update.message.reply_text(
                "ℹ️ Использование: /broadcast <сообщение>\n"
                "Пример: /broadcast Технические работы с 20:00 до 21:00"
            )
            return
            
        try:
            message = ' '.join(context.args)
            users = self.bot.db.get_users()
            
            sent = 0
            failed = 0
            for user_id in users:
                try:
                    await context.bot.send_message(
                        chat_id=int(user_id),
                        text=f"📢 *Объявление:*\n\n{message}",
                        parse_mode='Markdown'
                    )
                    sent += 1
                except Exception:
                    failed += 1
                    
            status = (
                "📨 *Статус рассылки:*\n\n"
                f"✅ Отправлено: {sent} пользователям\n"
                f"❌ Не доставлено: {failed} пользователям"
            )
            await update.message.reply_text(status, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при рассылке: {str(e)}")

    async def add_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.bot._is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ У вас нет прав для использования этой команды.")
            return

        if not context.args:
            await update.message.reply_text(
                "ℹ️ Использование: /addadmin <user_id>\n"
                "Пример: /addadmin 123456789"
            )
            return

        try:
            new_admin_id = int(context.args[0])
            if new_admin_id in self.bot.ADMIN_IDS:
                await update.message.reply_text("⚠️ Этот пользователь уже является администратором.")
                return

            self.bot.ADMIN_IDS.add(new_admin_id)
            self.bot.db.save_admin_ids(self.bot.ADMIN_IDS)
            await update.message.reply_text(f"✅ Пользователь {new_admin_id} добавлен как администратор.")
        except ValueError:
            await update.message.reply_text("❌ Некорректный ID пользователя.")

    async def remove_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.bot._is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ У вас нет прав для использования этой команды.")
            return

        if not context.args:
            await update.message.reply_text(
                "ℹ️ Использование: /removeadmin <user_id>\n"
                "Пример: /removeadmin 123456789"
            )
            return

        try:
            admin_id = int(context.args[0])
            if admin_id == 873278697:  # Защита главного админа
                await update.message.reply_text("⚠️ Невозможно удалить главного администратора.")
                return

            if admin_id not in self.bot.ADMIN_IDS:
                await update.message.reply_text("⚠️ Этот пользователь не является администратором.")
                return

            self.bot.ADMIN_IDS.remove(admin_id)
            self.bot.db.save_admin_ids(self.bot.ADMIN_IDS)
            await update.message.reply_text(f"✅ Пользователь {admin_id} удален из администраторов.")
        except ValueError:
            await update.message.reply_text("❌ Некорректный ID пользователя.")

    async def list_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.bot._is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ У вас нет прав для использования этой команды.")
            return

        admins_list = "\n".join([f"👤 `{admin_id}`" for admin_id in self.bot.ADMIN_IDS])
        await update.message.reply_text(
            f"📋 *Список администраторов:*\n\n{admins_list}",
            parse_mode='Markdown'
        ) 