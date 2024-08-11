from locust import HttpUser, task


class LoadTest(HttpUser):

    @task
    def write(self):
        filename = 'load.py'
        self.client.post("/files", files=[
            ('obj', (filename, open(filename, 'rb'), 'application/x-gtar')),
        ])

    @task
    def read(self):
        self.client.get("/files/7228441476399800320")