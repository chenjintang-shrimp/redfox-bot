"""Configurable card-rendering backend dispatch."""

from typing import Any

from httpx import AsyncClient

from renderer.skin_loader import render_template as render_skin_template
from utils.flt_mgr import apply_minifilters_async
from utils.html2image import html_to_image
from utils.variable import RENDERER_BACKEND, TAKUMI_ADDRESS, TAKUMI_ENDPOINT


async def render_card_image(
    view_name: str,
    data: dict[str, Any],
    *,
    skin: str,
    width: int,
    height: int | None,
) -> bytes:
    """Render raw card data through the configured backend."""
    if RENDERER_BACKEND == "playwright":
        processed_data = await apply_minifilters_async(view_name, data)
        html = await render_skin_template(skin, view_name, processed_data)
        return await html_to_image(html, width=width, height=height)

    if RENDERER_BACKEND == "takumi":
        return await _render_with_takumi(
            view_name,
            data,
            skin=skin,
            width=width,
            height=height,
        )

    raise ValueError(f"Unsupported renderer backend: {RENDERER_BACKEND}")


async def _render_with_takumi(
    view_name: str,
    data: dict[str, Any],
    *,
    skin: str,
    width: int,
    height: int | None,
) -> bytes:
    """POST raw renderer data to Takumi.

    The envelope intentionally carries raw API-derived data. Takumi's final
    request schema and response semantics remain an integration TODO; the
    provisional contract expects image bytes in the response body.
    """
    if not TAKUMI_ADDRESS:
        raise RuntimeError("renderer.takumi_address must be set for the takumi backend")
    if not TAKUMI_ENDPOINT:
        raise RuntimeError("renderer.takumi_endpoint must be set for the takumi backend")

    payload = {
        "renderer": view_name,
        "skin": skin,
        "width": width,
        "height": height,
        "data": data,
    }
    target_url = f"{TAKUMI_ADDRESS.rstrip('/')}/{TAKUMI_ENDPOINT.lstrip('/')}"
    async with AsyncClient(timeout=30.0) as client:
        response = await client.post(target_url, json=payload)
        response.raise_for_status()
        return response.content
