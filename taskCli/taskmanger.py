import psutil
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.live import Live

console = Console()

def format_bytes(size):
    return f"{size / (1024 ** 3):.2f} GB"

def get_cpu_panel():
    cpu_percentages = psutil.cpu_percent(percpu=True)
    table = Table(title="CPU Usage", expand=True)
    table.add_column("Core", justify="right")
    table.add_column("Usage (%)", justify="right")
    for i, perc in enumerate(cpu_percentages):
        table.add_row(f"Core {i+1}", f"{perc}%")
    total_cpu = psutil.cpu_percent()
    table.add_row("[bold]Total[/bold]", f"[bold]{total_cpu}%[/bold]")
    return Panel(table)

def get_memory_panel():
    mem = psutil.virtual_memory()
    text = (
        f"Total: {format_bytes(mem.total)}\n"
        f"Used: {format_bytes(mem.used)} ({mem.percent}%)\n"
        f"Free: {format_bytes(mem.available)}"
    )
    return Panel(text, title="RAM Usage")

def get_disk_panel():
    disk = psutil.disk_usage('/')
    text = (
        f"Total: {format_bytes(disk.total)}\n"
        f"Used: {format_bytes(disk.used)} ({disk.percent}%)\n"
        f"Free: {format_bytes(disk.free)}"
    )
    return Panel(text, title="Disk Usage")

def get_battery_panel():
    battery = psutil.sensors_battery()
    if battery:
        status = "Charging" if battery.power_plugged else "Discharging"
        text = f"{round(battery.percent,2)}% ({status})"
    else:
        text = "No Battery Detected"
    return Panel(text, title="Battery Status")

def get_temperature_panel():
    temps = psutil.sensors_temperatures()
    if not temps:
        return Panel("Temperature sensors not found", title="Temperatures")
    output = ""
    for name, entries in temps.items():
        output += f"[bold]{name}[/bold]\n"
        for entry in entries:
            output += f"  {entry.label or 'Sensor'}: {entry.current}°C\n"
    return Panel(output.strip(), title="Temperatures")

def render_dashboard():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="upper", ratio=2),
        Layout(name="lower", ratio=1)
    )

    layout["header"].update(
        Panel(f"[bold cyan]Python CLI Task Manager — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold cyan]")
    )
    layout["upper"].split_row(
        Layout(get_cpu_panel(), name="cpu"),
        Layout(get_memory_panel(), name="memory")
    )
    layout["lower"].split_row(
        Layout(get_disk_panel(), name="disk"),
        Layout(get_temperature_panel(), name="temps"),
        Layout(get_battery_panel(), name="battery")
    )
    return layout

if __name__ == "__main__":
    try:
        with Live(render_dashboard(), refresh_per_second=1, screen=True) as live:
            while True:
                time.sleep(1)
                live.update(render_dashboard())
    except KeyboardInterrupt:
        console.print("\n[red]Task Manager closed.[/red]")
