import os
import aiohttp
import aiofiles
import random
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def truncate(text):
    if len(text) <= 35:
        return text, ""
    words = text.split()
    first = ""
    second = ""
    for word in words:
        if len(first + " " + word) <= 35:
            first += " " + word
        else:
            second += " " + word
    return first.strip(), second.strip()

async def gen_thumb(video_id: str):
    try:
        cache_path = f"cache/{video_id}_player_style.png"
        if os.path.isfile(cache_path):
            return cache_path

        # YouTube info fetch
        results = VideosSearch(video_id, limit=1)
        for result in (await results.next())["result"]:
            title = result.get("title", "No Title")
            duration = result.get("duration", "Live")
            thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status != 200:
                    return None
                img_path = f"cache/thumb_{video_id}.png"
                f = await aiofiles.open(img_path, mode="wb")
                await f.write(await resp.read())
                await f.close()

        cover = Image.open(img_path).convert("RGBA")
        cover = cover.resize((600, 330))

        canvas = Image.new("RGBA", (1280, 720), (20, 20, 20, 255))
        canvas.paste(cover, (340, 60))

        draw = ImageDraw.Draw(canvas)
        font_title = ImageFont.truetype("AnieXEricaMusic/assets/font3.ttf", 38)
        font_small = ImageFont.truetype("AnieXEricaMusic/assets/font2.ttf", 26)

        # Title text
        line1, line2 = truncate(title)
        draw.text((380, 420), line1, font=font_title, fill="white")
        if line2:
            draw.text((380, 465), line2, font=font_title, fill="white")

        # Views
        draw.text((380, 515), f"YouTube | {views}", font=font_small, fill="white")

        # Progress bar
        progress_start = (380, 565)
        progress_end = (880, 565)
        percentage = random.uniform(0.1, 0.9)
        middle = int(progress_start[0] + ((progress_end[0] - progress_start[0]) * percentage))
        draw.line([progress_start, (middle, 565)], fill=(255, 0, 0), width=6)
        draw.line([(middle, 565), progress_end], fill=(180, 180, 180), width=4)

        # Duration
        draw.text((380, 580), "00:00", font=font_small, fill="white")
        draw.text((880, 580), duration, font=font_small, fill="white")

        os.remove(img_path)
        canvas.save(cache_path)
        return cache_path

    except Exception as e:
        logging.error(f"Thumbnail error: {e}")
        return None