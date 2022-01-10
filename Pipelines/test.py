
def launch(parent):
    print('This is from test pipeline')
    print(parent.bids.root_dir)
    print(parent.bids.number_of_subjects)
    print(parent.bids.IGNORED_SERIES)