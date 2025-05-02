from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # defines a random delay between requests

    @task
    def load_home_page(self):
        self.client.get("/", name="Home page")

    @task
    def load_health_check(self):
        self.client.get("/health", name="Health check")

    @task
    def load_about_page(self):
        self.client.get("/about")

    @task
    def load_api_page(self):
        self.client.get("/docs")

    @task
    def load_invalid_geometries(self):
        self.client.get("/invalid-geometries")
