"""Basic queue demo with simple string-keyed items.

Demonstrates:
- Queue rendering with custom content callback
- Sortable.js drag-and-drop reorder with server persistence
- Remove and clear operations
- Empty state display
- on_mutate callback for OOB item count update
"""

from fasthtml.common import Div, Span, P, APIRouter

from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import flex_display, grow, justify
from cjm_fasthtml_tailwind.utilities.spacing import m, p as pad
from cjm_fasthtml_tailwind.utilities.typography import font_size, truncate
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors, badge_sizes

from cjm_fasthtml_sortable_queue.config import SortableQueueConfig
from cjm_fasthtml_sortable_queue.html_ids import SortableQueueHtmlIds
from cjm_fasthtml_sortable_queue.models import SortableQueueUrls
from cjm_fasthtml_sortable_queue.rendering import render_sortable_queue
from cjm_fasthtml_sortable_queue.router import init_sortable_queue_router


# Sample data
SAMPLE_ITEMS = [
    {"id": "item_001", "name": "Introduction to Graph Theory"},
    {"id": "item_002", "name": "Chapter 1: Laying Plans"},
    {"id": "item_003", "name": "Chapter 2: Waging War"},
    {"id": "item_004", "name": "Chapter 3: Attack by Stratagem"},
    {"id": "item_005", "name": "Chapter 4: Tactical Dispositions"},
]

# OOB counter element ID
COUNTER_ID = "bq-item-counter"


def setup():
    """Set up the basic queue demo page."""
    config = SortableQueueConfig(prefix="bq")
    ids = SortableQueueHtmlIds(prefix="bq")

    # In-memory state (keyed by session — single session for demo)
    state = {"items": list(SAMPLE_ITEMS)}

    def get_items(sess):
        return list(state["items"])

    def set_items(sess, items):
        state["items"] = items

    def render_content(item, index):
        """Render item name as the custom content."""
        return Span(
            item["name"],
            cls=combine_classes(grow(), font_size.sm, truncate),
            title=item["name"]
        )

    def render_counter(items):
        """Render an OOB item count badge."""
        return Span(
            f"{len(items)} items in queue",
            id=COUNTER_ID,
            hx_swap_oob="outerHTML",
            cls=combine_classes(badge, badge_colors.primary, badge_sizes.sm)
        )

    def on_mutate(mutation_type, items, sess):
        """Return OOB counter update on any mutation."""
        return (render_counter(items),)

    # Initialize Tier 2 router
    sq_router, urls = init_sortable_queue_router(
        config=config,
        get_items=get_items,
        set_items=set_items,
        render_content=render_content,
        on_mutate=on_mutate,
        prefix="/bq",
    )

    def page_content():
        """Render the demo page."""
        current_items = state["items"]
        return Div(
            Div(
                P("Basic queue with simple string-keyed items.", cls=str(font_size.sm)),
                render_counter(current_items),
                cls=combine_classes(flex_display, justify.between, m.b(4))
            ),
            Div(
                render_sortable_queue(
                    config=config,
                    ids=ids,
                    urls=urls,
                    queue_items=current_items,
                    render_content=render_content,
                ),
                cls=combine_classes(flex_display, justify.center)
            ),
            cls=str(pad(4))
        )

    return dict(
        router=sq_router,
        page_content=page_content,
        title="Basic Queue",
        description="Basic queue with simple string-keyed items",
    )
