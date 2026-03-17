"""Demo application for cjm-fasthtml-sortable-queue library.

Showcases queue rendering, drag-and-drop reorder, remove, clear,
and keyboard navigation across demo pages.

Run with: python demo_app.py
"""


DEMO_PORT = 5035


def main():
    """Initialize sortable queue demos and start the server."""
    from fasthtml.common import fast_app, Div, H1, P, A, APIRouter

    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes
    from cjm_fasthtml_daisyui.utilities.semantic_colors import text_dui

    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
    from cjm_fasthtml_tailwind.core.base import combine_classes

    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout

    from cjm_fasthtml_sortable_queue.sortable_js import sortable_js_headers, generate_sortable_init_script

    import demos.basic_queue as bq_demo
    import demos.keyed_queue as kq_demo

    print("\n" + "=" * 70)
    print("Initializing cjm-fasthtml-sortable-queue Demo")
    print("=" * 70)

    app, rt = fast_app(
        pico=False,
        hdrs=[
            *get_daisyui_headers(),
            create_theme_persistence_script(),
            *sortable_js_headers(),
            generate_sortable_init_script(),
        ],
        title="Sortable Queue Demo",
        htmlkw={'data-theme': 'light'},
        secret_key="demo-secret-key"
    )

    router = APIRouter(prefix="")

    # -------------------------------------------------------------------------
    # Set up demos
    # -------------------------------------------------------------------------

    bq = bq_demo.setup()
    print(f"  Basic queue demo: {bq['title']}")

    kq = kq_demo.setup()
    print(f"  Keyed queue demo: {kq['title']}")

    # -------------------------------------------------------------------------
    # Page routes
    # -------------------------------------------------------------------------

    @router
    def index(request):
        """Homepage with demo overview."""

        def home_content():
            return Div(
                H1("Sortable Queue Demo",
                   cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

                P("Sortable.js-enhanced ordered queue panels with drag-and-drop "
                  "reorder, keyboard navigation, and HTMX-powered mutations.",
                  cls=combine_classes(font_size.lg, text_dui.base_content, m.b(8))),

                A("Open Basic Queue Demo",
                  href=demo_basic.to(),
                  cls=combine_classes(btn, btn_colors.primary, btn_sizes.lg)),

                cls=combine_classes(
                    container, max_w._4xl, m.x.auto, p(8), text_align.center
                )
            )

        return handle_htmx_request(
            request, home_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_basic(request):
        """Basic queue demo page."""
        return handle_htmx_request(
            request, bq['page_content'],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_keyed(request):
        """Keyed queue demo page with keyboard navigation."""
        return handle_htmx_request(
            request, kq['page_content'],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    # -------------------------------------------------------------------------
    # Navbar & route registration
    # -------------------------------------------------------------------------

    navbar = create_navbar(
        title="Sortable Queue Demo",
        nav_items=[
            ("Home", index),
            ("Basic Queue", demo_basic),
            ("Keyed Queue", demo_keyed),
        ],
        home_route=index,
        theme_selector=True
    )

    register_routes(app, router, bq['router'], kq['router'])

    # Debug output
    print("\n" + "=" * 70)
    print("Registered Routes:")
    print("=" * 70)
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
    print("=" * 70)
    print("Demo App Ready!")
    print("=" * 70 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    app = main()

    port = DEMO_PORT
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print(f"\n  http://{display_host}:{port}/              — Homepage")
    print(f"  http://{display_host}:{port}/demo_basic    — Basic queue demo")
    print(f"  http://{display_host}:{port}/demo_keyed   — Keyed queue demo")
    print()

    timer = threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    uvicorn.run(app, host=host, port=port)
