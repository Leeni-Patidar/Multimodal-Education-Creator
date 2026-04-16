import base64
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.schema import GenerateRequest
from services.image_service import generate_images
from services.llm_service import generate_text
from utils.prompt_builder import build_image_prompt, build_text_prompt

router = APIRouter()
logger = logging.getLogger(__name__)

# Thread pool for blocking I/O operations
executor = ThreadPoolExecutor(max_workers=2)


@router.post("/generate")
async def generate_content(req: GenerateRequest):
    try:
        logger.info(f"Generating content for topic: {req.topic}")

        text_prompt = build_text_prompt(req.topic, req.level)
        image_topic = req.image_prompt.strip() if req.image_prompt and req.image_prompt.strip() else req.topic
        image_prompt = build_image_prompt(image_topic, req.style)

        # Run text and image generation in parallel
        logger.info("Starting parallel content generation...")
        loop = asyncio.get_event_loop()
        
        text_output, image_bytes_list = await asyncio.gather(
            loop.run_in_executor(executor, generate_text, text_prompt),
            loop.run_in_executor(executor, generate_images, image_prompt, req.image_count),
            return_exceptions=False
        )

        images_base64 = [
            base64.b64encode(image_bytes).decode("utf-8")
            for image_bytes in image_bytes_list
            if image_bytes
        ]

        logger.info("Content generation completed successfully")
        return {
            "topic": req.topic,
            "explanation": text_output,
            "image": images_base64[0] if images_base64 else None,
            "images": images_base64,
        }
    except Exception as e:
        logger.exception(f"Error generating content: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to generate content"},
        )
