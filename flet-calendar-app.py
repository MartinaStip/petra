import flet as ft
from datetime import datetime, timedelta
import calendar
import csv
import os

def main(page: ft.Page):
    page.title = "Date Tracker"
    page.padding = 20
    page.scroll = "auto"
    
    csv_file = "dates.csv"
    
    # Aktuální datum
    today = datetime.now()
    selected_date = today
    current_month = today.month
    current_year = today.year
    
    # Text pro vybrané datum
    selected_text = ft.Text(
        f"Vybrané: {selected_date.strftime('%d.%m.%Y')}",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE
    )
    
    # Funkce pro vytvoření kalendáře
    def create_calendar():
        cal = calendar.monthcalendar(current_year, current_month)
        month_name = calendar.month_name[current_month]
        
        # Hlavička s měsícem a rokem
        header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=prev_month
            ),
            ft.Text(
                f"{month_name} {current_year}",
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=next_month
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Dny v týdnu
        weekdays = ft.Row([
            ft.Container(
                content=ft.Text(day, size=12, weight=ft.FontWeight.BOLD),
                width=45,
                alignment=ft.alignment.center
            )
            for day in ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Vytvoř řádky s dny
        weeks = []
        for week in cal:
            days_row = []
            for day in week:
                if day == 0:
                    # Prázdné místo
                    days_row.append(ft.Container(width=45, height=45))
                else:
                    # Den v měsíci
                    is_today = (day == today.day and 
                               current_month == today.month and 
                               current_year == today.year)
                    is_selected = (day == selected_date.day and 
                                  current_month == selected_date.month and 
                                  current_year == selected_date.year)
                    
                    days_row.append(
                        ft.Container(
                            content=ft.Text(str(day), size=16),
                            width=45,
                            height=45,
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.BLUE if is_selected else (ft.Colors.BLUE_100 if is_today else None),
                            border_radius=25,
                            on_click=lambda e, d=day: select_day(d)
                        )
                    )
            weeks.append(ft.Row(days_row, alignment=ft.MainAxisAlignment.CENTER))
        
        return ft.Column([header, weekdays] + weeks, spacing=5)
    
    # Funkce pro výběr dne
    def select_day(day):
        nonlocal selected_date
        selected_date = datetime(current_year, current_month, day)
        selected_text.value = f"Vybrané: {selected_date.strftime('%d.%m.%Y')}"
        calendar_container.content = create_calendar()
        page.update()
    
    # Funkce pro předchozí měsíc
    def prev_month(e):
        nonlocal current_month, current_year
        current_month -= 1
        if current_month < 1:
            current_month = 12
            current_year -= 1
        calendar_container.content = create_calendar()
        page.update()
    
    # Funkce pro další měsíc
    def next_month(e):
        nonlocal current_month, current_year
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
        calendar_container.content = create_calendar()
        page.update()
    
    # Funkce pro přidání data do CSV
    def add_date(e):
        dates = []
        if os.path.exists(csv_file):
            with open(csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                dates = [row[0] for row in reader]
        
        date_str = selected_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        dates.sort()
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for date in dates:
                writer.writerow([date])
        
        snack = ft.SnackBar(content=ft.Text(f"Přidáno: {selected_date.strftime('%d.%m.%Y')}"))
        page.snack_bar = snack
        snack.open = True
        page.update()
    
    # Tlačítko pro přidání
    add_button = ft.ElevatedButton(
        "Přidat datum",
        icon=ft.Icons.ADD,
        on_click=add_date,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
        )
    )
    
    # Kontejner pro kalendář
    calendar_container = ft.Container(
        content=create_calendar(),
        padding=10
    )
    
    # Rozložení
    page.add(
        ft.Column([
            ft.Text("Sledování dat", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            calendar_container,
            selected_text,
            add_button,
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)