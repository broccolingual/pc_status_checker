import platform as pl

import cpuid
import psutil as ps
import PySimpleGUI as gui


def main():
    # OS
    os_info = pl.system_alias(pl.system(), pl.release(), pl.version())

    # CPU
    cpu_name = cpuid.cpu_name()
    cpu_microarch = cpuid.cpu_microarchitecture()
    physical_cpu_count = ps.cpu_count(logical=False)
    logical_cpu_count = ps.cpu_count(logical=True)

    all_cpu_percent = ps.cpu_percent(interval=1)
    per_cpu_percent = ps.cpu_percent(interval=1, percpu=True)

    # RAM
    ram_amount = ps.virtual_memory().total
    ram_free = ps.virtual_memory().available
    ram_used = ps.virtual_memory().used
    ram_used_percent = ps.virtual_memory().percent

    # GUI
    os_frame = gui.Frame("OS", layout=[
        [gui.Text(f"{os_info[0]} {os_info[1]} build {os_info[2]}")],
    ])

    cpu_percent_list = []
    for i, per in enumerate(per_cpu_percent):
        cpu_percent_list.append([f"Core {i}", f"{per}%"])

    cpu_frame = gui.Frame("CPU", layout=[
        [gui.Text(f"{cpu_name}")],
        [gui.Text(f"Micro Architecture : {cpu_microarch[0]}")],
        [gui.Text(
            f"Physical / Logical : {physical_cpu_count} Core / {logical_cpu_count} Core")],
        [gui.Text(f"Used : {all_cpu_percent}%", key="-all_cpu_percent-")],
        [gui.Table(cpu_percent_list, headings=[
                   "Core", "Percent"], text_color="#000000", background_color="#cccccc", alternating_row_color="#ffffff", key="-per_cpu_percent-")],
    ])

    mem_frame = gui.Frame("Memory", layout=[
        [gui.Text(f"RAM Capacity: {round(ram_amount/1024/1024/1024, 1)}GB")],
        [gui.Table([[f"{round(ram_used/1024/1024/1024, 1)}GB", f"{round(ram_free/1024/1024/1024, 1)}GB", f"{ram_used_percent}%"]], headings=["Used", "Available",
                   "Percent"], num_rows=1, text_color="#000000", background_color="#ffffff", key="-ram_status-")]
    ])

    layout = [
        [os_frame],
        [cpu_frame],
        [mem_frame],
    ]

    show_window(layout)


def show_window(layout):
    try:
        window = gui.Window("PC STATUS CHECKER", layout)
        while True:
            e, v = window.read(timeout=300, timeout_key='-UPDATE-')
            print(f"{e=} | {v=}")
            if e == gui.WIN_CLOSED or e == None:
                break
            elif e in "-UPDATE-":
                # Update CPU Percent
                window["-all_cpu_percent-"].update(
                    f"Used : {ps.cpu_percent(interval=1)}%")

                cpu_percent_list = []
                for i, per in enumerate(ps.cpu_percent(interval=1, percpu=True)):
                    cpu_percent_list.append([f"Core {i}", f"{per}%"])
                window["-per_cpu_percent-"].update(values=cpu_percent_list)

                # Update RAM Status
                window["-ram_status-"].update(values=[[f"{round(ps.virtual_memory().used/1024/1024/1024, 1)}GB",
                                                       f"{round(ps.virtual_memory().available/1024/1024/1024, 1)}GB", f"{ps.virtual_memory().percent}%"]])
    except Exception as e:
        pass
    finally:
        window.close()


if __name__ == "__main__":
    main()
