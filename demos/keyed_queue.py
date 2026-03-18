"""Keyed queue demo with composite keys and keyboard navigation.

Demonstrates:
- Composite key_fn for items with multiple identity fields
- Self-contained keyboard system (standalone, no parent)
- Delete/Backspace to remove focused item
- Shift+Arrow to reorder focused item
- Keyboard navigation with focus ring
- data_attributes for extracting item identity from focused row
"""

from fasthtml.common import Div, Span, P, Button, APIRouter

from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, grow, justify, items as items_align
)
from cjm_fasthtml_tailwind.utilities.spacing import m, p as pad
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_family, truncate
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_styles, badge_sizes
from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui

from cjm_fasthtml_sortable_queue.config import SortableQueueConfig, get_item_key
from cjm_fasthtml_sortable_queue.html_ids import SortableQueueHtmlIds
from cjm_fasthtml_sortable_queue.models import SortableQueueUrls
from cjm_fasthtml_sortable_queue.rendering import render_sortable_queue
from cjm_fasthtml_sortable_queue.handlers import (
    handle_reorder, handle_reorder_by_direction, handle_remove, handle_clear
)
from cjm_fasthtml_sortable_queue.keyboard import create_queue_keyboard_system

from cjm_fasthtml_tailwind.utilities.effects import ring
from cjm_fasthtml_daisyui.utilities.semantic_colors import ring_dui


# Sample data with composite keys
SAMPLE_ITEMS = [
    {"provider_id": "whisper", "record_id": "job_a1b2", "text": "Introduction segment"},
    {"provider_id": "whisper", "record_id": "job_c3d4", "text": "Chapter one opening"},
    {"provider_id": "voxtral", "record_id": "job_e5f6", "text": "Battle strategy notes"},
    {"provider_id": "gemini", "record_id": "job_g7h8", "text": "Tactical overview"},
    {"provider_id": "whisper", "record_id": "job_i9j0", "text": "Concluding remarks"},
]


def setup():
    """Set up the keyed queue demo page."""
    config = SortableQueueConfig(
        prefix="kq",
        key_fn=lambda item: f"{item['provider_id']}:{item['record_id']}",
        queue_title="Sources",
    )
    ids = SortableQueueHtmlIds(prefix="kq")

    # In-memory state
    state = {"items": list(SAMPLE_ITEMS)}

    def render_content(item, index):
        """Render record ID + provider badge as custom content."""
        return Div(
            Span(
                item["record_id"],
                cls=combine_classes(font_size.sm, font_family.mono, truncate),
                title=item["text"]
            ),
            Span(
                item["provider_id"],
                cls=combine_classes(badge, badge_styles.ghost, badge_sizes.xs, m.l(2))
            ),
            cls=combine_classes(flex_display, items_align.center, grow())
        )

    # Build render_kwargs for consistent rendering across handlers
    render_kwargs = {}

    # Router for HTMX endpoints
    router = APIRouter(prefix="/kq")

    # We need urls before creating routes — build them manually
    urls = SortableQueueUrls(
        reorder="/kq/reorder",
        remove="/kq/remove",
        clear="/kq/clear",
    )

    @router
    async def reorder(request, sess):
        """Handle drag-drop reorder or keyboard reorder."""
        form_data = await request.form()
        new_key_order = form_data.getlist("item")

        # Check if this is a keyboard reorder (has direction param from vals_map)
        direction = form_data.get("direction", "")
        # Focused item key comes from data_attributes=("key",) hidden input
        focused_key = form_data.get("key", "")

        if direction and focused_key:
            # Keyboard reorder
            updated, panel = handle_reorder_by_direction(
                config, ids, urls, state["items"], focused_key, direction,
                render_content, **render_kwargs
            )
        else:
            # Drag-drop reorder
            updated, panel = handle_reorder(
                config, ids, urls, state["items"], new_key_order,
                render_content, **render_kwargs
            )
        state["items"] = updated
        return panel

    @router
    async def remove(request, sess, key: str = ""):
        """Handle item removal."""
        updated, panel = handle_remove(
            config, ids, urls, state["items"], key,
            render_content, **render_kwargs
        )
        state["items"] = updated
        return panel

    @router
    async def clear(sess):
        """Handle clear all."""
        updated, panel = handle_clear(config, ids, urls, render_content, **render_kwargs)
        state["items"] = updated
        return panel

    # Keyboard system
    queue_kb = create_queue_keyboard_system(
        config=config,
        ids=ids,
        urls=urls,
        zone_focus_classes=(str(ring(1)), str(ring_dui.secondary)),
        item_focus_classes=None,
        data_attributes=("key",),
        show_hints=True,
    )

    def page_content():
        """Render the demo page."""
        current_items = state["items"]
        return Div(
            P("Composite-key queue with keyboard navigation. "
              "Use Up/Down to navigate, Shift+Arrow to reorder, Delete to remove.",
              cls=str(font_size.sm)),
            Div(
                Div(
                    render_sortable_queue(
                        config=config,
                        ids=ids,
                        urls=urls,
                        queue_items=current_items,
                        render_content=render_content,
                    ),
                    # Keyboard system elements
                    queue_kb.script,
                    queue_kb.hidden_inputs,
                    queue_kb.action_buttons,
                    queue_kb.hints,
                ),
                cls=combine_classes(flex_display, justify.center, m.t(4))
            ),
            cls=str(pad(4))
        )

    return dict(
        router=router,
        page_content=page_content,
        title="Keyed Queue",
        description="Queue with composite keys and keyboard navigation",
    )
