# Telegram Referral Bot

Бот отслеживает приглашения в канал и ведёт статистику.

## Запуск локально
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

## Развёртывание на Render.com
1. Создай репозиторий на GitHub и залей все файлы
2. На Render — New → Web Service → подключи репозиторий
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python bot.py`