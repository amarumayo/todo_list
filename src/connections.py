def connect_signals(parent):
    # events
    parent.ui.submit_button.clicked.connect(parent.on_submit_button_push)
    parent.ui.delete_button.clicked.connect(parent.on_delete_button_push)
    parent.ui.table.itemSelectionChanged.connect(parent.on_row_select)
