pauseDuration = 1000


class MapPOM:
    def __init__(self, page, base_url) -> None:
        self.page = page
        self.base_url = base_url

    def navigate(self, urlParam=""):
        response = self.page.goto(self.base_url + "/map/" + urlParam)
        self.page.wait_for_timeout(
            pauseDuration
        )  # wait for some time to make sure the map code has loaded
        return response

    def check_layer_checkbox(self, layerName):
        self.page.get_by_label(layerName).check()
        self.page.wait_for_timeout(
            pauseDuration
        )  # wait for some time to make sure the data loads

    def zoom_map(self, zoomLevel):
        result = self.page.evaluate(
            "() => {try{mapControllers.map.map.setZoom("
            + str(zoomLevel)
            + ")} catch(e){return e.message}}"
        )
        print(result)

    def centre_map_over(self, x, y):
        result = self.page.evaluate(
            "() => {try{mapControllers.map.map.setCenter(["
            + str(x)
            + ","
            + str(y)
            + "])} catch(e){return e.message}}"
        )
        print(result)

    def click_map_centre(self):
        mapWidth = self.page.evaluate("() => mapControllers.map.map.getCanvas().width")
        mapHeight = self.page.evaluate(
            "() => mapControllers.map.map.getCanvas().height"
        )
        self.page.get_by_label("Map").click(
            position={"x": mapWidth / 2, "y": mapHeight / 2}
        )
        self.page.wait_for_timeout(pauseDuration)  # wait for potential popup

    def wait_for_map_layer(self, layer, attempts=10, check_interval=10):
        for i in range(attempts):
            isHidden = self.page.evaluate(
                f'() => mapControllers.map.map.getLayer("{layer}").isHidden()'
            )
            if isHidden is False:
                return True
            self.page.wait_for_timeout(check_interval)
        assert False, f"Layer {layer} did not appear on the map"

    def wait_for_popup(self, attempts=10, check_interval=100):
        for i in range(attempts):
            isHidden = (
                self.page.get_by_test_id("map").locator("div.app-popup").is_hidden()
            )
            if isHidden is False:
                return True
            self.page.wait_for_timeout(check_interval)
        zoom = self.page.evaluate("() => mapControllers.map.map.getZoom()")
        center = self.page.evaluate("() => mapControllers.map.map.getCenter()")
        assert False, f"Popup did not appear on the map as {center} at zoom {zoom}"

    def wait_for_layer_controls_to_load(self, attempts=10, check_interval=500):
        for i in range(attempts):
            isHidden = (
                self.page.get_by_test_id("map")
                .locator("button.dl-map__close-btn")
                .is_hidden()
            )
            if isHidden is False:
                return True
            self.page.wait_for_timeout(check_interval)
        assert False, "layer controls did not load"
