class A:
    def __init__(self, a):
        self.a = a
        self.task = self

a = A(1)
print(a.task.a)