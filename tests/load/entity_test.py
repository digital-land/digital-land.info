from locust import HttpUser, task, between


class EntityLoadTestUser(HttpUser):
    wait_time = between(1, 3)

    valid_entity_id = 31000
    sample_dataset = "border"
    sample_typology = "geography"

    @task
    def get_entity_html(self):
        self.client.get(f"/entity/{self.valid_entity_id}")

    @task
    def get_entity_json(self):
        self.client.get(f"/entity/{self.valid_entity_id}.json")

    @task
    def get_entity_geojson(self):
        self.client.get(f"/entity/{self.valid_entity_id}.geojson")

    @task
    def search_entities_json(self):
        self.client.get(
            f"/entity.json?dataset={self.sample_dataset}&typology={self.sample_typology}"
        )

    @task
    def search_entities_geojson(self):
        self.client.get(
            f"/entity.geojson?dataset={self.sample_dataset}&typology={self.sample_typology}"
        )
