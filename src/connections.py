def connect_signals(window):
    # events
    window.submit_button.clicked.connect(window.on_submit_button_push)
    window.delete_button.clicked.connect(window.on_delete_button_push)
    window.table.itemSelectionChanged.connect(window.on_row_select)
