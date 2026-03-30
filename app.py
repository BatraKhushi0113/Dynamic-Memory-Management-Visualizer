import tkinter as tk
from tkinter import ttk, messagebox
from algorithms import fifo, lru, optimal
from utils.logger import log_event

def run_app():
    root = tk.Tk()
    root.title("Intelligent Memory Management Visualizer")
    root.state("zoomed")

    # ================= COLORS =================
    BG = "#0f172a"
    CARD = "#1e293b"
    CARD2 = "#111827"
    TEXT = "#f8fafc"
    MUTED = "#94a3b8"
    BLUE = "#3b82f6"
    GREEN = "#22c55e"
    RED = "#ef4444"
    PURPLE = "#8b5cf6"
    ORANGE = "#f59e0b"
    CYAN = "#06b6d4"

    root.configure(bg=BG)

    # ================= TITLE =================
    title = tk.Label(
        root,
        text="Intelligent Memory Management Visualizer",
        font=("Segoe UI", 26, "bold"),
        bg=BG,
        fg=TEXT
    )
    title.pack(pady=(12, 0))

    subtitle = tk.Label(
        root,
        text="Paging • Virtual Memory • FIFO • LRU • Visualization",
        font=("Segoe UI", 12),
        bg=BG,
        fg=MUTED
    )
    subtitle.pack(pady=(0, 12))

    # ================= MAIN LAYOUT =================
    # ========================= SCROLLABLE MAIN =========================
    container = tk.Frame(root, bg=BG)
    container.pack(fill="both", expand=True)

    main_canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
    v_scroll = ttk.Scrollbar(container, orient="vertical", command=main_canvas.yview)
    h_scroll = ttk.Scrollbar(container, orient="horizontal", command=main_canvas.xview)

    main_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")
    main_canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = tk.Frame(main_canvas, bg=BG)

    window = main_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def update_scroll(event=None):
       main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    def resize(event):
       main_canvas.itemconfig(window, width=max(event.width, 1600))

    scroll_frame.bind("<Configure>", update_scroll)
    main_canvas.bind("<Configure>", resize)

# Mouse scroll
    def on_mousewheel(event):
       main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(event):
       main_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    main_canvas.bind_all("<MouseWheel>", on_mousewheel)
    main_canvas.bind_all("<Shift-MouseWheel>", on_shift_mousewheel)

# LEFT + RIGHT
    left = tk.Frame(scroll_frame, bg=BG)
    left.grid(row=0, column=0, sticky="nsew", padx=(10, 5))

    right = tk.Frame(scroll_frame, bg=BG)
    right.grid(row=0, column=1, sticky="nsew", padx=(5, 10))

    scroll_frame.grid_columnconfigure(0, weight=1)
    scroll_frame.grid_columnconfigure(1, weight=2)

    def create_card(parent, title_text):
        card = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1, highlightbackground="#334155")
        header = tk.Label(card, text=title_text, font=("Segoe UI", 14, "bold"), bg=CARD, fg=TEXT, anchor="w")
        header.pack(fill="x", padx=12, pady=(10, 6))
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        return card, body

    # ================= INPUT CARD =================
    input_card, input_body = create_card(left, "📥 Memory Input")
    input_card.pack(fill="x", pady=(0, 12))

    tk.Label(input_body, text="Page Reference String", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
    pages_entry = tk.Entry(input_body, width=35, font=("Segoe UI", 11), bg=CARD2, fg=TEXT, insertbackground=TEXT, relief="flat")
    pages_entry.grid(row=1, column=0, padx=(0, 10), pady=(0, 10))

    tk.Label(input_body, text="Frames", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 4))
    frame_entry = tk.Entry(input_body, width=10, font=("Segoe UI", 11), bg=CARD2, fg=TEXT, insertbackground=TEXT, relief="flat")
    frame_entry.grid(row=1, column=1, pady=(0, 10))

    pages_entry.insert(0, "1,2,3,1,4,5,2,1,2,3")
    frame_entry.insert(0, "3")

    # ================= BUTTONS =================
    btn_frame = tk.Frame(input_body, bg=CARD)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky="w")

    def styled_button(parent, text, color, cmd):
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8,
            cursor="hand2"
        )

    # ================= METRICS CARD =================
    metrics_card, metrics_body = create_card(left, "📊 Live Metrics")
    metrics_card.pack(fill="x", pady=(0, 12))

    metric_labels = {}

    metric_names = [
        "Algorithm", "Page Faults", "Hits", "Hit Ratio", "Frames Used"
    ]

    for i, name in enumerate(metric_names):
        box = tk.Frame(metrics_body, bg=CARD2, bd=0)
        box.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="nsew")
        tk.Label(box, text=name, bg=CARD2, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        val = tk.Label(box, text="--", bg=CARD2, fg=TEXT, font=("Segoe UI", 16, "bold"))
        val.pack(anchor="w", padx=10, pady=(0, 8))
        metric_labels[name] = val

    metrics_body.grid_columnconfigure(0, weight=1)
    metrics_body.grid_columnconfigure(1, weight=1)

    # ================= EVENT LOG =================
    log_card, log_body = create_card(left, "📜 Event Log")
    log_card.pack(fill="both", expand=True)

    log_box = tk.Text(
        log_body,
        height=16,
        bg=CARD2,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        wrap="word",
        font=("Consolas", 10),
        padx=10,
        pady=10
    )
    log_box.pack(fill="both", expand=True)

    # ================= MEMORY VISUAL =================
    visual_card, visual_body = create_card(right, "🧠 Memory Frame Visualization")
    visual_card.pack(fill="x", pady=(0, 12))

    canvas = tk.Canvas(visual_body, height=360, bg=CARD2, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    # ========================= GANTT CHART =========================
    gantt_card, gantt_body = create_card(right, "📊 Memory Access Timeline (Gantt Chart)")
    gantt_card.pack(fill="x", pady=(0, 12))

    gantt_canvas = tk.Canvas(gantt_body, height=120, bg=CARD2, highlightthickness=0)
    gantt_canvas.pack(fill="x")

    
    # ================= COMPARISON DASHBOARD =================
    compare_card, compare_body = create_card(right, "📈 Algorithm Comparison")
    compare_card.pack(fill="both", expand=True, pady=(0, 12))

    comparison_tree = ttk.Treeview(compare_body, columns=("Algorithm", "Faults", "Hits", "Hit Ratio"), show="headings", height=6)
    for col in ("Algorithm", "Faults", "Hits", "Hit Ratio"):
        comparison_tree.heading(col, text=col)
        comparison_tree.column(col, anchor="center", width=140)
    comparison_tree.pack(fill="x", expand=True)

    # ================= DETAILED OUTPUT =================
    output_card, output_body = create_card(right, "📄 Detailed Output")
    output_card.pack(fill="both", expand=True)

    output_text = tk.Text(
        output_body,
        height=12,
        bg=CARD2,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        wrap="none",
        font=("Consolas", 10),
        padx=10,
        pady=10
    )
    output_scroll_y = ttk.Scrollbar(output_body, orient="vertical", command=output_text.yview)
    output_scroll_x = ttk.Scrollbar(output_body, orient="horizontal", command=output_text.xview)
    output_text.configure(yscrollcommand=output_scroll_y.set, xscrollcommand=output_scroll_x.set)

    output_text.grid(row=0, column=0, sticky="nsew")
    output_scroll_y.grid(row=0, column=1, sticky="ns")
    output_scroll_x.grid(row=1, column=0, sticky="ew")
    output_body.grid_rowconfigure(0, weight=1)
    output_body.grid_columnconfigure(0, weight=1)

    # ================= FUNCTIONS =================
    def parse_input():
        try:
            pages = [int(x.strip()) for x in pages_entry.get().split(",") if x.strip() != ""]
            frames = int(frame_entry.get())

            if frames <= 0:
                raise ValueError

            return pages, frames
        except:
            messagebox.showerror("Input Error", "Please enter valid page sequence and frame count.")
            return None, None

    def clear_outputs():
        canvas.delete("all")
        log_box.delete("1.0", "end")
        output_text.delete("1.0", "end")
        for item in comparison_tree.get_children():
            comparison_tree.delete(item)

    def update_metrics(result):
        metric_labels["Algorithm"].config(text=result["name"])
        metric_labels["Page Faults"].config(text=str(result["faults"]))
        metric_labels["Hits"].config(text=str(result["hits"]))
        metric_labels["Hit Ratio"].config(text=f"{result['hit_ratio']:.2f}%")
        metric_labels["Frames Used"].config(text=str(result["capacity"]))

    def draw_memory(result):
        canvas.delete("all")
        history = result["history"]
        pages = result["pages"]
        capacity = result["capacity"]

        cell_w = 80
        cell_h = 45
        start_x = 90
        start_y = 40

        # Header pages
        for i, p in enumerate(pages):
            x = start_x + i * cell_w
            canvas.create_text(x + cell_w/2, start_y - 20, text=str(p), fill=TEXT, font=("Segoe UI", 10, "bold"))

        # Frame rows
        for r in range(capacity):
            y = start_y + r * cell_h
            canvas.create_text(40, y + cell_h/2, text=f"F{r}", fill=MUTED, font=("Segoe UI", 10, "bold"))

            for c in range(len(history)):
                x = start_x + c * cell_w
                canvas.create_rectangle(x, y, x + cell_w, y + cell_h, fill="#1d4ed8", outline="#334155")

                val = ""
                if r < len(history[c]):
                    val = str(history[c][r])

                canvas.create_text(x + cell_w/2, y + cell_h/2, text=val, fill="white", font=("Segoe UI", 11, "bold"))


    def draw_gantt(result):
        gantt_canvas.delete("all")

        pages = result["pages"]

        start_x = 20
        y = 40
        height = 40
        width_per_page = 70

        colors = ["#3b82f6", "#8b5cf6", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4"]

        for i, page in enumerate(pages):
            x1 = start_x + i * width_per_page
            x2 = x1 + width_per_page

            color = colors[page % len(colors)]

            gantt_canvas.create_rectangle(x1, y, x2, y + height, fill=color, outline="white")
            gantt_canvas.create_text((x1+x2)/2, y+height/2, text=f"P{page}", fill="white")

            gantt_canvas.create_text(x1, y+height+15, text=str(i), fill=TEXT)

        gantt_canvas.create_text(
            start_x + len(pages)*width_per_page,
            y+height+15,
           text=str(len(pages)),
           fill=TEXT
        )

    def show_output(result):
        output_text.delete("1.0", "end")

        output_text.insert("end", f"ALGORITHM: {result['name']}\n")
        output_text.insert("end", "=" * 70 + "\n\n")
        output_text.insert("end", f"Reference String : {result['pages']}\n")
        output_text.insert("end", f"Frames           : {result['capacity']}\n")
        output_text.insert("end", f"Page Faults      : {result['faults']}\n")
        output_text.insert("end", f"Hits             : {result['hits']}\n")
        output_text.insert("end", f"Hit Ratio        : {result['hit_ratio']:.2f}%\n\n")

        output_text.insert("end", "MEMORY STATES:\n")
        output_text.insert("end", "-" * 70 + "\n")

        for i, state in enumerate(result["history"]):
            output_text.insert("end", f"Step {i+1:02d} | Page {result['pages'][i]} -> {state}\n")

    def show_log(result):
        log_box.delete("1.0", "end")
        for line in result["events"]:
            log_event(log_box, line)

    def add_to_comparison(result):
        comparison_tree.insert("", "end", values=(
            result["name"],
            result["faults"],
            result["hits"],
            f"{result['hit_ratio']:.2f}%"
        ))

    def run_fifo():
        pages, frames = parse_input()
        if pages is None:
            return

        clear_outputs()
        result = fifo.run(pages, frames)
        update_metrics(result)
        draw_memory(result)
        show_output(result)
        show_log(result)
        add_to_comparison(result)
        draw_gantt(result)

    def run_lru():
        pages, frames = parse_input()
        if pages is None:
            return

        clear_outputs()
        result = lru.run(pages, frames)
        update_metrics(result)
        draw_memory(result)
        show_output(result)
        show_log(result)
        add_to_comparison(result)
        draw_gantt(result)
    
    def run_optimal():
       pages, frames = parse_input()
       if pages is None:
           return

       clear_outputs()
       result = optimal.run(pages, frames)

       update_metrics(result)
       draw_memory(result)
       show_output(result)
       show_log(result)
       add_to_comparison(result)
       draw_gantt(result)

    def compare_all():
        pages, frames = parse_input()
        if pages is None:
            return

        clear_outputs()

        fifo_result = fifo.run(pages, frames)
        lru_result = lru.run(pages, frames)
        opt_result = optimal.run(pages, frames)

        add_to_comparison(fifo_result)
        add_to_comparison(lru_result)
        add_to_comparison(opt_result)

        best = min([fifo_result, lru_result, opt_result],key=lambda x: x["faults"])
        

        update_metrics(best)
        draw_memory(best)
        draw_gantt(best)
        show_output(best)
        show_log(best)
        log_event(log_box, f"Best Algorithm: {best['name']}")

    # ================= BUTTONS ATTACH =================
    styled_button(btn_frame, "Run FIFO", BLUE, run_fifo).pack(side="left", padx=6)
    styled_button(btn_frame, "Run LRU", PURPLE, run_lru).pack(side="left", padx=6)
    styled_button(btn_frame, "Run OPTIMAL", ORANGE, run_optimal).pack(side="left", padx=6)
    styled_button(btn_frame, "Compare All", GREEN, compare_all).pack(side="left", padx=6)

    root.mainloop()