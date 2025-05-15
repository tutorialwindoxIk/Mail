from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import aiohttp, aiofiles, os, random
from youtubesearchpython.__future__ import VideosSearch

async def gen_stylish_thumb(video_id: str):
    try:
        cache_path = f"cache/{video_id}_modern_ui.png"
        if os.path.isfile(cache_path):
            return cache_path

        # Get video details
        results = VideosSearch(video_id, limit=1)
        result = (await results.next())["result"][0]
        title = result.get("title", "No Title")
        duration = result.get("duration", "Live")
        thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status != 200:
                    return None
                img_path = f"cache/thumb_{video_id}.png"
                f = await aiofiles.open(img_path, mode="wb")
                await f.write(await resp.read())
                await f.close()

        thumb = Image.open(img_path).convert("RGBA")

        # Blurred full background
        bg = thumb.resize((1280, 720)).filter(ImageFilter.GaussianBlur(25))
        bg = ImageEnhance.Brightness(bg).enhance(0.4)

        # Center card
        card = Image.new("RGBA", (900, 500), (255, 255, 255, 200))
        card = card.filter(ImageFilter.GaussianBlur(1))

        # Rounded corners for card
        mask = Image.new("L", card.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([0, 0, 900, 500], 60, fill=255)
        card.putalpha(mask)

        # Paste card
        bg.paste(card, (190, 110), card)

        # Draw inside card
        draw = ImageDraw.Draw(bg)
        font_title = ImageFont.truetype("AnieXEricaMusic/assets/font3.ttf", 42)
        font_views = ImageFont.truetype("AnieXEricaMusic/assets/font2.ttf", 28)

        # Resize and round the thumbnail
        small_thumb = thumb.resize((500, 280))
        thumb_mask = Image.new("L", (500, 280), 0)
        ImageDraw.Draw(thumb_mask).rounded_rectangle([0, 0, 500, 280], 25, fill=255)
        bg.paste(small_thumb, (390, 130), thumb_mask)

        # Title
        short_title = title if len(title) <= 35 else title[:32] + "..."
        draw.text((400, 430), short_title, font=font_title, fill="black")
        draw.text((400, 480), f"YouTube | {views}", font=font_views, fill="black")

        # Progress bar
        draw.line([(400, 520), (900, 520)], fill=(160, 160, 160), width=4)
        progress_x = random.randint(400, 880)
        draw.ellipse([progress_x - 5, 515 - 5, progress_x + 5, 515 + 5], fill="red")

        # Time labels
        draw.text((400, 535), "00:00", font=font_views, fill="black")
        draw.text((850, 535), duration, font=font_views, fill="black")

        # Control buttons: just placeholders with text, you can replace with icons
        icons = ["shuffle", "prev", "play", "next", "repeat"]
        positions = [430, 500, 570, 640, 710]
        for i, icon in enumerate(icons):
            draw.text((positions[i], 580), icon[0].upper(), font=font_title, fill="black")

        os.remove(img_path)
        bg.save(cache_path)
        return cache_path

    except Exception as e:
        import logging
        logging.exception(e)
        return None