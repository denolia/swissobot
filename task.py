class Task:
    status = False
    due_date = None
    category = None
    text = None
    link = ""

    def __init__(self, task_text):
        self.text = task_text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text
