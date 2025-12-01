import flet as ft

#ft.Page is the type/class that holds things like title, layout, controls (buttons, text, etc.)
def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Text field, default value 0
    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    # Functions of what happens after click = event handlers; e is for EVENT
    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    # Outline of the page + liking event handlers to the events
    # Controls = buttons, text fields etc.
    page.add(
        ft.Row(
            [
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

# Run the app
ft.app(main)