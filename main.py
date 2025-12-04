import flet as ft
from config import c_main
from cycle_tracker import CycleTracker

matplotlib.use("Agg")

def main(page: ft.Page):
    page.title = "PEriodTRAcker"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize tracker
    tracker = CycleTracker()
    
    # Navigation functions
    def navigate_to_data(e):
        page.go("/data")
    
    def navigate_to_home(e):
        page.go("/")
    
    # Event handlers
    def add_today(e):
        if not tracker.add_date(today):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Already there \N{THUMBS UP SIGN}"),
                open=True)
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Date added successfully!"),
                open=True)
        route_change(page.route)
        page.update()
    
    def add_selected(e):
        date_str = e.control.value.strftime('%Y-%m-%d')
        if not tracker.add_date(date_str):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Already there \N{THUMBS UP SIGN}"),
                open=True)
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Date added successfully!"),
                open=True)
        route_change(page.route)
        page.update()
    
    def delete_date_handler(date_str):
        def handler(e):
            # Confirmation dialog
            def close_dialog(e):
                dialog.open = False
                page.update()
            
            def confirm_delete(e):
                if tracker.delete_date(date_str):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Date deleted successfully!"),
                        open=True)
                    dialog.open = False
                    route_change(page.route)
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Error deleting date"),
                        open=True)
                page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Delete Date"),
                content=ft.Text(f"Are you sure you want to delete {date_str}?"),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        
        return handler
    
    # Data table 
    def build_data_table():
        """Build the data table with delete buttons"""
        all_dates = tracker.dates.sort_values("date", ascending=False)['date'].tolist()
        
        if len(all_dates) == 0:
            return ft.Text("No dates recorded yet", size=16)
        
        rows = []
        for date_str in all_dates:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(date_str)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=c_main,
                                tooltip="Delete this date",
                                on_click=delete_date_handler(date_str)
                            )
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("All recorded dates", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
        )
    
    # UI elements (buttons)
    add_today_button = ft.FilledButton(
        text="Add today",
        on_click=lambda e: add_today(e),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor=c_main,
        )
    )

    choose_date_button = ft.FilledButton(
        text="Pick another date",
        icon=ft.Icons.CALENDAR_MONTH,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=c_main,
        ),
        on_click=lambda e: page.open(
            ft.DatePicker(
            first_date=datetime(year=2000, month=10, day=1),
            last_date=datetime.now(),
            on_change=add_selected,
            confirm_text="Add date",
            )
        )
    )

    data_button = ft.FilledButton(
        text="View & edit data",
        icon=ft.Icons.ANALYTICS,
        on_click=navigate_to_data,
        style=ft.ButtonStyle(
        color=ft.Colors.WHITE,
        bgcolor=c_main,
        )
    )

    # Route change handler
    def route_change(route):
        page.views.clear()
        
        # Main page
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(
                        title=ft.Text("PEriodTRAcker"),
                        bgcolor=c_main,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Column([
                        ft.Row(
                            [ft.Text(
                                f"Estimated next date: {tracker.pred_date}", 
                                #color=c_main,
                                weight=ft.FontWeight.BOLD)],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [ft.Image(
                                src_base64=tracker.plot_pred(),
                                width=600,
                                height=300,
                            )],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [ft.Text(f"Last date: {tracker.dates['date'].iloc[-1] if len(tracker.dates) > 0 else 'N/A'}")],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(
                            content=ft.Row(
                                [add_today_button, choose_date_button],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.symmetric(vertical = 50),
                        ),
                        ft.Row(
                            [data_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ])
                ],
            )
        )
        
        # Data page
        if page.route == "/data":
            page.views.append(
                ft.View(
                    "/data",
                    [
                        ft.AppBar(                    # just to place the back arrow, no text
                            title=ft.Text(""),
                            bgcolor=ft.Colors.WHITE,
                            color=c_main,
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=navigate_to_home
                            ),
                        ),
                        ft.Column([
                            ft.Row(
                                [ft.Image(
                                    src_base64=tracker.plot_raw(),
                                    width=600,
                                    height=300,
                                )],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [build_data_table()],
                                #padding=20
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO)
                    ],
                )
            )
        
        page.update()
    
    # Set up routing
    page.on_route_change = route_change
    page.go(page.route)


ft.app(main)