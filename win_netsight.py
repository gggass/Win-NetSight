"""
Win-NetSight: Windows 网络洞察者
一个用于实时监控 Windows 网络连接的终端仪表盘。

结合了用于底层数据采集的 C++ 后端和用于 TUI 展示的 Python/Rich。
"""

import subprocess
import json
import time
import sys
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def generate_layout() -> Layout:
    """初始化 TUI 网格布局。"""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    layout["main"].split_row(
        Layout(name="left", size=40),
        Layout(name="right")
    )
    layout["right"].split(
        Layout(name="connections_tcp"),
        Layout(name="connections_udp")
    )
    return layout

def make_header() -> Panel:
    """创建页眉面板。"""
    return Panel(
        Align.center(
            Text("Win-NetSight: Windows Network Insight", justify="center", style="bold green"),
            vertical="middle",
        ),
        style="bold blue on #000080",
    )

def make_connection_table(title: str, connections: list, style: str) -> Panel:
    """创建连接表格面板。"""
    table = Table(title=title, border_style=style, show_header=True, header_style="bold white")
    table.add_column("Protocol", style="cyan", no_wrap=True)
    table.add_column("Local Address", style="magenta", no_wrap=True)
    table.add_column("Local Port", style="yellow", no_wrap=True)
    table.add_column("Remote Address", style="green", no_wrap=True)
    table.add_column("Remote Port", style="blue", no_wrap=True)
    table.add_column("PID", style="red", no_wrap=True)
    table.add_column("State", style="white", no_wrap=True)

    for conn in connections:
        state_str = str(conn.get("state", "N/A"))
        # 简化 TCP 状态显示，实际应用中可能需要更详细的映射
        if conn["protocol"] == "TCP":
            tcp_states = {
                1: "CLOSED", 2: "LISTEN", 3: "SYN_SENT", 4: "SYN_RCVD",
                5: "ESTABLISHED", 6: "FIN_WAIT1", 7: "FIN_WAIT2", 8: "CLOSE_WAIT",
                9: "CLOSING", 10: "LAST_ACK", 11: "TIME_WAIT", 12: "DELETE_TCB"
            }
            state_str = tcp_states.get(conn.get("state"), f"UNKNOWN({conn.get("state")})")
        
        table.add_row(
            conn.get("protocol", "N/A"),
            conn.get("local_addr", "N/A"),
            conn.get("local_port", "N/A"),
            conn.get("remote_addr", "N/A"),
            conn.get("remote_port", "N/A"),
            str(conn.get("pid", "N/A")),
            state_str
        )
    return Panel(table, title=title, border_style=style)

def main():
    layout = generate_layout()
    layout["header"].update(make_header())

    process = None
    try:
        # 确定 C++ 采集器二进制文件的名称
        # 在 Windows 上，它将是 netsight_core.exe
        binary = "netsight_core.exe"
        
        # 启动 C++ 采集器进程
        process = subprocess.Popen(
            [binary],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 跳过预热行
        process.stdout.readline()

        with Live(layout, screen=True, refresh_per_second=4) as live:
            while True:
                line = process.stdout.readline()
                if not line:
                    # 检查进程是否意外终止
                    if process.poll() is not None:
                        console.log("[bold red]Error:[/bold red] Collector process terminated unexpectedly.")
                    break
                try:
                    data = json.loads(line)
                    connections = data.get("connections", [])

                    tcp_conns = [c for c in connections if c.get("protocol") == "TCP"]
                    udp_conns = [c for c in connections if c.get("protocol") == "UDP"]

                    # 更新 UI 各个部分
                    layout["connections_tcp"].update(make_connection_table("TCP Connections", tcp_conns, "cyan"))
                    layout["connections_udp"].update(make_connection_table("UDP Endpoints", udp_conns, "magenta"))
                    
                    status_panel = Panel(
                        Text(f"Last sync: {time.strftime("%H:%M:%S")}", justify="center"),
                        title="Status", border_style="green"
                    )
                    layout["left"].update(status_panel)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    console.log(f"Error: {e}")

    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] netsight_core.exe not found. Please compile the C++ code first.")
    except KeyboardInterrupt:
        pass
    finally:
        if process and process.poll() is None:
            process.terminate()

if __name__ == "__main__":
    main()
