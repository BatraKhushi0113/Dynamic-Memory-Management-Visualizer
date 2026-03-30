def log_event(log_box, text):
    log_box.insert("end", text + "\n")
    log_box.see("end")