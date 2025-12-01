import flet as ft
import matplotlib.pyplot as plt
import numpy as np

def main(page: ft.Page):
    page.title = "Flet + Matplotlib Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Example data
    x = np.arange(10)
    y = np.random.randint(1, 10, size=10)

    # Create Matplotlib figure
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='blue')
    ax.set_title("Test Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Create Flet MatplotlibChart widget
    chart = ft.MatplotlibChart(fig, expand=True)

    # Add chart to the page
    page.add(
        ft.Column(
            [
                ft.Text("Flet + Matplotlib Chart Example"),
                chart
            ],
        )
    )

    # Run the app
ft.app(target=main)