import flet as ft
from datetime import datetime, timedelta
import json
import os

class MenstrualTracker:
    def __init__(self):
        self.data_file = "menstrual_data.json"
        self.cycles = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.cycles, f)
    
    def add_cycle(self, date_str):
        self.cycles.append(date_str)
        self.cycles.sort(reverse=True)  # Nejnovější první
        self.save_data()
    
    def delete_cycle(self, date_str):
        if date_str in self.cycles:
            self.cycles.remove(date_str)
            self.save_data()
    
    def predict_next(self):
        if len(self.cycles) < 2:
            return None, None
        
        # Vypočítej průměrnou délku cyklu
        intervals = []
        for i in range(len(self.cycles) - 1):
            date1 = datetime.strptime(self.cycles[i], "%Y-%m-%d")
            date2 = datetime.strptime(self.cycles[i + 1], "%Y-%m-%d")
            intervals.append(abs((date1 - date2).days))
        
        avg_cycle = sum(intervals) / len(intervals)
        
        # Predikce dalšího data
        last_date = datetime.strptime(self.cycles[0], "%Y-%m-%d")
        next_date = last_date + timedelta(days=int(avg_cycle))
        
        return next_date, avg_cycle

def main(page: ft.Page):
    page.title = "Kalendář menstruace"
    page.padding = 20
    page.scroll = "adaptive"
    
    tracker = MenstrualTracker()
    
    # Funkce pro přidání data
    def add_date(e):
        if date_picker.value:
            date_str = date_picker.value.strftime("%Y-%m-%d")
            tracker.add_cycle(date_str)
            update_cycles_list()
            update_prediction()
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("✅ Záznam přidán!"), bgcolor=ft.Colors.GREEN)
            )
    
    # UI komponenty
    date_picker = ft.DatePicker(
        on_change=add_date,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(date_picker)
    
    prediction_text = ft.Text(
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PINK_700
    )
    
    cycle_length_text = ft.Text(size=16, color=ft.Colors.GREY_700)
    
    cycles_list = ft.Column(spacing=10)
    
    def update_prediction():
        next_date, avg_cycle = tracker.predict_next()
        if next_date:
            prediction_text.value = f"🗓️ Příští menstruace: {next_date.strftime('%d.%m.%Y')}"
            cycle_length_text.value = f"📊 Průměrná délka cyklu: {avg_cycle:.1f} dní"
        else:
            prediction_text.value = "⚠️ Přidej alespoň 2 záznamy pro predikci"
            cycle_length_text.value = ""
        page.update()
    
    def update_cycles_list():
        cycles_list.controls.clear()
        for cycle_date in tracker.cycles:
            date_obj = datetime.strptime(cycle_date, "%Y-%m-%d")
            
            def make_delete_handler(date_str):
                def handler(e):
                    tracker.delete_cycle(date_str)
                    update_cycles_list()
                    update_prediction()
                return handler
            
            cycles_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.PINK_400),
                            ft.Text(
                                date_obj.strftime("%d.%m.%Y"),
                                size=16,
                                weight=ft.FontWeight.W_500
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                on_click=make_delete_handler(cycle_date)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.PINK_50,
                )
            )
        page.update()
    
    def open_date_picker(e):
        date_picker.open = True
        page.update()
    
    # Hlavní layout
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "🌸 Kalendář menstruace",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PINK_700
                    ),
                    ft.Divider(height=20, color=ft.Colors.PINK_200),
                    
                    # Predikce
                    ft.Container(
                        content=ft.Column([
                            prediction_text,
                            cycle_length_text,
                        ]),
                        padding=15,
                        border_radius=10,
                        bgcolor=ft.Colors.PINK_100,
                        margin=ft.margin.only(bottom=20)
                    ),
                    
                    # Tlačítko pro přidání
                    ft.ElevatedButton(
                        "➕ Přidat datum menstruace",
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                        on_click=open_date_picker,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.PINK_400,
                        ),
                        width=300,
                        height=50,
                    ),
                    
                    ft.Divider(height=30, color=ft.Colors.PINK_200),
                    
                    # Seznam záznamů
                    ft.Text(
                        "Historie záznamů:",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PINK_700
                    ),
                    cycles_list,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        )
    )
    
    # Inicializace
    update_cycles_list()
    update_prediction()

# Spuštění aplikace
ft.app(target=main)