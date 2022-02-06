from email.policy import default
import platform as pl
from concurrent.futures import ThreadPoolExecutor

import cpuid
import psutil as ps
import PySimpleGUI as gui

FONT_DEFAULT = ("Segoe UI", 11)


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

    # GUI Layout
    gui.theme("Default1")

    os_frame = gui.Frame("OS", font=FONT_DEFAULT, layout=[
        [gui.Text(f"{os_info[0]} {os_info[1]} build {os_info[2]}",
                  font=FONT_DEFAULT)],
    ])

    cpu_percent_list = []
    for i, per in enumerate(per_cpu_percent):
        cpu_percent_list.append([f"Core {i}", f"{per}%"])

    cpu_frame = gui.Frame("CPU", font=FONT_DEFAULT, layout=[
        [gui.Text(f"{cpu_name}", font=FONT_DEFAULT)],
        [gui.Text(
            f"Micro Architecture : {cpu_microarch[0]}", font=FONT_DEFAULT)],
        [gui.Text(
            f"Physical / Logical : {physical_cpu_count} Core / {logical_cpu_count} Core", font=FONT_DEFAULT)],
        [gui.Text(f"Used : {all_cpu_percent}%",
                  key="-all_cpu_percent-", font=FONT_DEFAULT)],
        [gui.Table(cpu_percent_list, headings=[
                   "Core", "Percent"], text_color="#000000", background_color="#cccccc", alternating_row_color="#ffffff", key="-per_cpu_percent-", font=FONT_DEFAULT)],
    ])

    mem_frame = gui.Frame("Memory", font=FONT_DEFAULT, layout=[
        [gui.Text(
            f"RAM Capacity: {round(ram_amount/1024/1024/1024, 1)}GB", font=FONT_DEFAULT)],
        [gui.Table([[f"{round(ram_used/1024/1024/1024, 1)}GB", f"{round(ram_free/1024/1024/1024, 1)}GB", f"{ram_used_percent}%"]], headings=["Used", "Available",
                   "Percent"], num_rows=1, text_color="#000000", background_color="#ffffff", key="-ram_status-", font=FONT_DEFAULT)]
    ])

    layout = [
        [os_frame],
        [cpu_frame],
        [mem_frame],
    ]

    show_window(layout)


def update_all_cpu_percent():
    return ps.cpu_percent(interval=1)


def update_per_cpu_percent():
    cpu_percent_list = []
    for i, per in enumerate(ps.cpu_percent(interval=1, percpu=True)):
        cpu_percent_list.append([f"Core {i}", f"{per}%"])
    return cpu_percent_list


def update_memory_status():
    return [[f"{round(ps.virtual_memory().used/1024/1024/1024, 1)}GB",
             f"{round(ps.virtual_memory().available/1024/1024/1024, 1)}GB", f"{ps.virtual_memory().percent}%"]]


def show_window(layout):
    thread_pool = ThreadPoolExecutor(max_workers=10)  # make thread pool

    try:
        window = gui.Window("PC STATUS CHECKER", layout)
        while True:
            e, v = window.read(timeout=100, timeout_key='-UPDATE-')
            print(f"{e=} | {v=}")  # for debug
            if e == gui.WIN_CLOSED or e == None:
                break
            elif e in "-UPDATE-":
                # UPDATE STATUS
                future_memory_status = thread_pool.submit(update_memory_status)
                future_all_cpu_status = thread_pool.submit(
                    update_all_cpu_percent)
                future_per_cpu_percent = thread_pool.submit(
                    update_per_cpu_percent)

                window["-ram_status-"].update(
                    values=future_memory_status.result())
                window["-all_cpu_percent-"].update(
                    f"Used : {future_all_cpu_status.result()}%")
                window["-per_cpu_percent-"].update(
                    values=future_per_cpu_percent.result())

    except Exception as e:
        print(e)

    finally:
        window.close()  # close window
        thread_pool.shutdown()  # shutdown thread pool


if __name__ == "__main__":
    main()
