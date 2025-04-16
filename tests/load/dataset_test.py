from locust import HttpUser, task, between


class DatasetLoadTestUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def list_datasets_html(self):
        self.client.get("/dataset")

    @task
    def list_datasets_json(self):
        self.client.get("/dataset.json")

    @task
    def get_dataset(self):
        self.client.get("/dataset/border")
