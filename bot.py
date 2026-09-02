from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from telegram import InputMediaPhoto, InputMediaVideo, Update
from telegram.constants import ChatAction
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


LOGGER = logging.getLogger(__name__)
URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
ALLOWED_HOSTS = {"pinterest.com", "www.pinterest.com", "pin.it"}
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}


@dataclass(frozen=True)
class Settings:
    token: str
    max_downloads: int = 10
    max_file_mb: int = 49
    download_timeout: int = 180
    cookies_file: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("BOT_TOKEN is required")
        return cls(
            token=token,
            max_downloads=max(1, min(int(os.getenv("MAX_DOWNLOADS", "10")), 50)),
            max_file_mb=max(1, int(os.getenv("MAX_FILE_MB", "49"))),
            download_timeout=max(30, int(os.getenv("DOWNLOAD_TIMEOUT", "180"))),
            cookies_file=os.getenv("COOKIES_FILE") or None,
        )


def extract_pinterest_url(text: str | None) -> str | None:
    if not text:
        return None
    match = URL_RE.search(text)
    if not match:
        return None
    url = match.group(0).rstrip(".,!?;:)]}\"")
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"}:
        return None
    if host not in ALLOWED_HOSTS and not host.endswith(".pinterest.com"):
        return None
    return url


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in PHOTO_EXTENSIONS:
        return "photo"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    mime, _ = mimetypes.guess_type(path.name)
    if mime and mime.startswith("image/"):
        return "photo"
    if mime and mime.startswith("video/"):
        return "video"
    return "document"


async def download(url: str, target: Path, settings: Settings) -> list[Path]:
    command = [
        "gallery-dl",
        "--dest", str(target),
        "--range", f"1-{settings.max_downloads}",
        "--no-mtime",
    ]
    if settings.cookies_file:
        command.extend(["--cookies", settings.cookies_file])
    command.append(url)

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, stderr = await asyncio.wait_for(process.communicate(), settings.download_timeout)
    except TimeoutError:
        process.kill()
        await process.communicate()
        raise RuntimeError("The download timed out. Please try again.")

    files = sorted(path for path in target.rglob("*") if path.is_file() and path.stat().st_size)
    if process.returncode != 0 and not files:
        detail = stderr.decode(errors="replace").strip().splitlines()
        LOGGER.warning("gallery-dl failed: %s", detail[-1] if detail else "unknown error")
        raise RuntimeError("Pinterest could not provide downloadable media for this link.")
    if not files:
        raise RuntimeError("No downloadable media was found.")
    return files[: settings.max_downloads]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Hi! Send me a Pinterest pin or board link and I’ll download its media for you.\n\n"
            "Use /help for details."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Send one public Pinterest URL in a message. I can return photos and videos.\n"
            "Private or login-only content may require cookies configured by the bot owner."
        )


async def send_files(update: Update, files: list[Path], settings: Settings) -> None:
    assert update.message is not None
    max_bytes = settings.max_file_mb * 1024 * 1024
    eligible = [path for path in files if path.stat().st_size <= max_bytes]
    skipped = len(files) - len(eligible)

    # Albums support only photos/videos and at most 10 items.
    media_paths = [p for p in eligible if classify(p) in {"photo", "video"}]
    if len(media_paths) > 1:
        handles = [path.open("rb") for path in media_paths[:10]]
        try:
            album = []
            for path, handle in zip(media_paths[:10], handles):
                album.append(InputMediaPhoto(handle) if classify(path) == "photo" else InputMediaVideo(handle))
            await update.message.reply_media_group(album)
        finally:
            for handle in handles:
                handle.close()
        sent = set(media_paths[:10])
    else:
        sent = set()

    for path in eligible:
        if path in sent:
            continue
        with path.open("rb") as handle:
            kind = classify(path)
            if kind == "photo":
                await update.message.reply_photo(handle)
            elif kind == "video":
                await update.message.reply_video(handle, supports_streaming=True)
            else:
                await update.message.reply_document(handle, filename=path.name)

    if skipped:
        await update.message.reply_text(
            f"Skipped {skipped} file(s) larger than the {settings.max_file_mb} MB limit."
        )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    url = extract_pinterest_url(update.message.text)
    if not url:
        await update.message.reply_text("Please send a valid Pinterest URL (pinterest.com or pin.it).")
        return

    settings: Settings = context.application.bot_data["settings"]
    status = await update.message.reply_text("Downloading…")
    await update.message.chat.send_action(ChatAction.TYPING)
    workdir = Path(tempfile.mkdtemp(prefix="pinterest-bot-"))
    try:
        files = await download(url, workdir, settings)
        await status.edit_text(f"Found {len(files)} file(s). Uploading…")
        await send_files(update, files, settings)
        await status.delete()
    except (RuntimeError, TelegramError) as exc:
        LOGGER.exception("Request failed")
        await status.edit_text(f"Sorry, I couldn’t process that link. {exc}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOGGER.exception("Unhandled exception", exc_info=context.error)


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
    settings = Settings.from_env()
    application = Application.builder().token(settings.token).build()
    application.bot_data["settings"] = settings
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    application.add_error_handler(error_handler)
    LOGGER.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
