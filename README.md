# Pinterest Downloader Telegram Bot V2

[فارسی](#فارسی) · [English](#english)

A production-friendly Telegram bot that downloads photos and videos from public Pinterest pins and boards. Built with Python, `python-telegram-bot`, and `gallery-dl`.

## English

### Features

- Downloads public Pinterest pins, videos, and boards
- Accepts `pinterest.com`, regional Pinterest subdomains, and `pin.it`
- Sends multiple photos/videos as Telegram albums
- Configurable download count, file-size limit, and timeout
- Optional Netscape-format cookies for login-only content
- Safe subprocess execution without a shell
- Automatic temporary-file cleanup
- Docker and Docker Compose support
- Unit tests and GitHub Actions

### Requirements

- Python 3.11 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Quick start

```bash
git clone https://github.com/iArvin0/pinterest-telegram-bot.git
cd pinterest-telegram-bot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, put your token in `BOT_TOKEN`, then export the variables and run:

```bash
set -a
source .env
set +a
python bot.py
```

On Windows PowerShell:

```powershell
$env:BOT_TOKEN="YOUR_TOKEN"
python bot.py
```

### Run with Docker

```bash
cp .env.example .env
# Edit .env first
docker compose up -d --build
docker compose logs -f
```

### Configuration

| Variable | Default | Description |
| --- | ---: | --- |
| `BOT_TOKEN` | required | Token provided by BotFather |
| `MAX_DOWNLOADS` | `10` | Maximum files fetched per request (hard cap: 50) |
| `MAX_FILE_MB` | `49` | Maximum size of each outgoing file |
| `DOWNLOAD_TIMEOUT` | `180` | Download timeout in seconds |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `COOKIES_FILE` | empty | Optional path to a Netscape cookies file |

Never commit `.env` or `cookies.txt`; both are ignored by Git.

### Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

### Commands

- `/start` — introduction
- `/help` — usage instructions
- Send a Pinterest URL — download and receive available media

### Deployment notes

The bot uses long polling, so it works on any always-on VPS or container platform. Some free hosting services suspend background workers. If Telegram rejects a large upload, lower `MAX_FILE_MB`. Pinterest can change its pages at any time; update `gallery-dl` when extraction stops working.

### Responsible use

Download only content you own or have permission to use. Respect copyright, privacy, Pinterest's terms, and Telegram's terms. This project is not affiliated with Pinterest or Telegram.

---

## فارسی

این پروژه یک ربات تلگرام آمادهٔ اجرا برای دانلود عکس و ویدئو از پین‌ها و بردهای عمومی Pinterest است. ربات با پایتون، `python-telegram-bot` و `gallery-dl` ساخته شده است.

### امکانات

- دانلود عکس، ویدئو و بردهای عمومی پینترست
- پشتیبانی از `pinterest.com`، زیردامنه‌های منطقه‌ای و `pin.it`
- ارسال چند عکس یا ویدئو به شکل آلبوم تلگرام
- محدودیت قابل تنظیم برای تعداد، حجم فایل و زمان دانلود
- امکان استفاده از فایل کوکی برای محتوای نیازمند ورود
- اجرای امن دانلودر بدون shell
- حذف خودکار فایل‌های موقت
- آماده برای Docker و Docker Compose
- دارای تست و GitHub Actions

### پیش‌نیازها

- پایتون ۳.۱۱ یا جدیدتر
- توکن ربات تلگرام از [BotFather](https://t.me/BotFather)

### نصب سریع

```bash
git clone https://github.com/iArvin0/pinterest-telegram-bot.git
cd pinterest-telegram-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

فایل `.env` را باز کنید و توکن را در `BOT_TOKEN` قرار دهید، سپس:

```bash
set -a
source .env
set +a
python bot.py
```

### اجرا با Docker

```bash
cp .env.example .env
# ابتدا مقدار BOT_TOKEN را در .env وارد کنید
docker compose up -d --build
docker compose logs -f
```

### تنظیمات

| متغیر | مقدار پیش‌فرض | توضیح |
| --- | ---: | --- |
| `BOT_TOKEN` | اجباری | توکن دریافتی از BotFather |
| `MAX_DOWNLOADS` | `10` | حداکثر تعداد فایل هر درخواست؛ سقف داخلی ۵۰ |
| `MAX_FILE_MB` | `49` | حداکثر حجم هر فایل ارسالی |
| `DOWNLOAD_TIMEOUT` | `180` | مهلت دانلود به ثانیه |
| `LOG_LEVEL` | `INFO` | سطح گزارش‌گیری برنامه |
| `COOKIES_FILE` | خالی | مسیر اختیاری فایل کوکی با فرمت Netscape |

فایل‌های `.env` و `cookies.txt` را در GitHub قرار ندهید؛ این فایل‌ها در `.gitignore` هستند.

### اجرای تست‌ها

```bash
pip install -r requirements-dev.txt
pytest -q
```

### دستورات ربات

- `/start` — معرفی ربات
- `/help` — راهنمای استفاده
- ارسال لینک Pinterest — دانلود و ارسال فایل‌های موجود

### نکات استقرار

ربات از Long Polling استفاده می‌کند و روی VPS یا سرویس کانتینری همیشه‌روشن اجرا می‌شود. بعضی سرویس‌های رایگان پردازش پس‌زمینه را متوقف می‌کنند. اگر تلگرام فایل بزرگی را رد کرد، مقدار `MAX_FILE_MB` را کاهش دهید. اگر ساختار Pinterest تغییر کرد و دانلود متوقف شد، پکیج `gallery-dl` را به‌روزرسانی کنید.

### استفاده مسئولانه

فقط محتوایی را دانلود کنید که مالک آن هستید یا اجازهٔ استفاده از آن را دارید. قوانین کپی‌رایت، حریم خصوصی و شرایط Pinterest و Telegram را رعایت کنید. این پروژه وابسته به Pinterest یا Telegram نیست.

## License

MIT
