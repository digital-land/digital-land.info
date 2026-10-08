import { getDatasetMinZoom } from "./datasetMinZoomLevels.js";

/**
 * Messaging to inform user to zoom in to view datasets which have
 * zoom limit (For example: Title Boundaries)
 */
export default class DatasetZoomAlerts {
  constructor(mapController, layerControls) {
    this.mapController = mapController;
    this.layerControls = layerControls;

    this.dismissed = {};
    this.alertElements = {};

    this._container = document.createElement('div');
    this._container.classList.add('dl-zoom-alerts');
    this.mapController.map.getContainer().appendChild(this._container);

    this.mapController.map.on('zoom', this.update.bind(this));
    this.update();
  }

  relevantLayerOptions() {
    return this.layerControls.layerOptions.filter(
      (option) => getDatasetMinZoom(option.getDatasetName()) !== null
    );
  }

  update() {
    const zoom = this.mapController.map.getZoom();

    this.relevantLayerOptions().forEach((option) => {
      const dataset = option.getDatasetName();
      const minZoom = getDatasetMinZoom(dataset);
      const tilesVisible = zoom >= minZoom;

      if (!option.isChecked()) {
        this.dismissed[dataset] = false;
        this.hideAlert(dataset);
        return;
      }

      if (tilesVisible) {
        this.hideAlert(dataset);
        return;
      }

      if (this.dismissed[dataset]) {
        this.hideAlert(dataset);
        return;
      }

      this.showAlert(dataset, option.layer.name);
    });
  }

  static iconInfoSvg() {
    return `
      <svg class="dl-zoom-alert__icon" role="presentation" focusable="false" viewBox="0 0 30 30" height="20" width="20">
        <path fill-rule="evenodd" clip-rule="evenodd" fill="currentColor" d="M10.2165 3.45151C11.733 2.82332 13.3585 2.5 15 2.5C16.6415 2.5 18.267 2.82332 19.7835 3.45151C21.3001 4.07969 22.6781 5.00043 23.8388 6.16117C24.9996 7.3219 25.9203 8.69989 26.5485 10.2165C27.1767 11.733 27.5 13.3585 27.5 15C27.5 18.3152 26.183 21.4946 23.8388 23.8388C21.4946 26.183 18.3152 27.5 15 27.5C13.3585 27.5 11.733 27.1767 10.2165 26.5485C8.69989 25.9203 7.3219 24.9996 6.16117 23.8388C3.81696 21.4946 2.5 18.3152 2.5 15C2.5 11.6848 3.81696 8.50537 6.16117 6.16117C7.3219 5.00043 8.69989 4.07969 10.2165 3.45151ZM16.3574 22.4121H13.6621V12.95H16.3574V22.4121ZM13.3789 9.20898C13.3789 8.98763 13.4212 8.7793 13.5059 8.58398C13.5905 8.38216 13.7044 8.20964 13.8477 8.06641C13.9974 7.91667 14.1699 7.79948 14.3652 7.71484C14.5605 7.63021 14.7721 7.58789 15 7.58789C15.2214 7.58789 15.4297 7.63021 15.625 7.71484C15.8268 7.79948 15.9993 7.91667 16.1426 8.06641C16.2923 8.20964 16.4095 8.38216 16.4941 8.58398C16.5788 8.7793 16.6211 8.98763 16.6211 9.20898C16.6211 9.43685 16.5788 9.64844 16.4941 9.84375C16.4095 10.0391 16.2923 10.2116 16.1426 10.3613C15.9993 10.5046 15.8268 10.6185 15.625 10.7031C15.4297 10.7878 15.2214 10.8301 15 10.8301C14.7721 10.8301 14.5605 10.7878 14.3652 10.7031C14.1699 10.6185 13.9974 10.5046 13.8477 10.3613C13.7044 10.2116 13.5905 10.0391 13.5059 9.84375C13.4212 9.64844 13.3789 9.43685 13.3789 9.20898Z" />
      </svg>
    `;
  }

  showAlert(dataset, layerName) {
    if (this.alertElements[dataset]) return;

    const alert = document.createElement('div');
    alert.classList.add('dl-zoom-alert');
    alert.setAttribute('role', 'region');
    alert.setAttribute('aria-label', `Information: zoom in to view ${layerName} data layer`);
    alert.innerHTML = `
      ${DatasetZoomAlerts.iconInfoSvg()}
      <p class="dl-zoom-alert__content">Zoom in to view ${layerName} data layer.</p>
      <button type="button" class="dl-zoom-alert__dismiss">
        <span class="govuk-visually-hidden">Dismiss zoom message for ${layerName}</span>
      </button>
    `;

    const dismissButton = alert.querySelector('.dl-zoom-alert__dismiss');
    dismissButton.addEventListener('click', () => this.dismiss(dataset));

    this._container.appendChild(alert);
    this.alertElements[dataset] = alert;
  }

  hideAlert(dataset) {
    const element = this.alertElements[dataset];
    if (!element) return;

    element.remove();
    delete this.alertElements[dataset];
  }

  dismiss(dataset) {
    this.dismissed[dataset] = true;
    this.hideAlert(dataset);
  }
}
