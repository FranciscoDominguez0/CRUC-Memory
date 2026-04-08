import reflex as rx

config = rx.Config(
    app_name="CRUC_Memory",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)