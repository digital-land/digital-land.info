import {defaultPaintOptions} from "./defaultPaintOptions.js";

export default class LayerControls {
    constructor (mapController, source, layers, availableLayers, options) {
      this.mapController = mapController;
      this.tileSource = source;
      this.layers = layers;
      this.availableLayers = availableLayers;

      this._container = document.createElement('div');
      this.layerOptions = [];

		  const styleClasses = this._container.classList;
      styleClasses.add('maplibregl-ctrl')

      this.layerURLParamName = options.layerURLParamName || 'dataset';
      this.redirectURLParamNames = options.redirectURLParamNames || [];

      // listen for changes to URL
      var boundSetControls = this.toggleLayersBasedOnUrl.bind(this);
      window.addEventListener('popstate', function (event) {
        boundSetControls();
      });

      this.replaceRedirectParamNames();
    }

    onAdd(map) {
      const sidePanel = document.createElement('div');
      sidePanel.classList.add('dl-map__side-panel');
      sidePanel.setAttribute('tabindex', '-1');
      sidePanel.setAttribute('role', 'dialog');
      sidePanel.setAttribute('aria-hidden', 'false');
      sidePanel.setAttribute('open', 'true');
      sidePanel.setAttribute('aria-modal', 'true');

      const heading = document.createElement('div');
      heading.classList.add('dl-map__side-panel__heading');

      const h3 = document.createElement('h3');
      h3.classList.add('govuk-heading-s', 'govuk-!-margin-bottom-0');
      h3.textContent = 'Data layers';

      heading.appendChild(h3);
      sidePanel.appendChild(heading);

      const content = document.createElement('div');
      content.classList.add('dl-map__side-panel__content');
      this.$sidePanelContent = content;

      const checkboxes = document.createElement('div');
      checkboxes.classList.add('govuk-checkboxes');
      checkboxes.setAttribute('data-module', `layer-controls-${this.mapController.mapId}}`);

      const filterGroup = document.createElement('div');
      filterGroup.classList.add('dl-filter-group__auto-filter');

      const filterLabel = document.createElement('label');
      filterLabel.setAttribute('for', 'input-71108');
      filterLabel.classList.add('govuk-label', 'govuk-visually-hidden');
      filterLabel.textContent = 'Filter Show only';

      this.$textbox = document.createElement('input');
      this.$textbox.setAttribute('id', 'input-71108');
      this.$textbox.classList.add('govuk-input', 'dl-filter-group__auto-filter__input');
      this.$textbox.setAttribute('type', 'text');
      this.$textbox.setAttribute('aria-describedby', 'checkbox-filter-71108');
      this.$textbox.setAttribute('aria-controls', 'checkboxes-71108');
      this.$textbox.addEventListener('input', this.filterCheckboxes.bind(this));

      filterGroup.appendChild(filterLabel);
      filterGroup.appendChild(this.$textbox);
      checkboxes.appendChild(filterGroup);

      const list = document.createElement('ul');
      list.classList.add('govuk-list');
      list.setAttribute('style', 'height: 400px;')
      list.setAttribute('data-module', 'layer-toggles');
      list.setAttribute('role', 'group');



      this.layerOptions = this.layers.map((layer) => {
        return new LayerOption(layer, this.availableLayers[layer.dataset], this);
      });

      this.layerOptions.forEach(option => list.appendChild(option.element));

      checkboxes.appendChild(list);
      content.appendChild(checkboxes);
      sidePanel.appendChild(content);

      this.$sidePanel = sidePanel;

      const closeButton = document.createElement('button');
      closeButton.classList.add('dl-map__close-btn');
      closeButton.dataset.action = 'close';
      const closeLabel = document.createElement('span');
      closeLabel.textContent = 'Close layer panel';
      closeLabel.classList.add('govuk-visually-hidden');
      closeButton.appendChild(closeLabel);
      sidePanel.appendChild(closeButton);

      const boundTogglePanel = this.togglePanel.bind(this);
      closeButton.addEventListener('click', boundTogglePanel);
      this.$closeBtn = closeButton;

      const openButton = document.createElement('button');
      openButton.classList.add('dl-map__open-btn', 'js-hidden');
      openButton.dataset.action = 'open';
      const openLabel = document.createElement('span');
      openLabel.textContent = 'Open layer panel';
      openLabel.classList.add('govuk-visually-hidden');
      openButton.appendChild(openLabel);
      this.mapController.map.getContainer().appendChild(openButton);

      openButton.addEventListener('click', boundTogglePanel);
      this.$openBtn = openButton;

      this._container.appendChild(sidePanel);

      // initial set up of controls (default or urlParams)
      const urlParams = (new URL(document.location)).searchParams;
      if (!urlParams.has(this.layerURLParamName)) {
        // if not set then use default checked controls
        this.updateUrl();
      } else {
        // use URL params if available
        this.toggleLayersBasedOnUrl();
      }

      return this._container;
    }

    replaceRedirectParamNames() {
      const urlParams = (new URL(document.location)).searchParams;
      this.redirectURLParamNames.forEach(param => {
        if (urlParams.has(param)) {
          let values = urlParams.getAll(param);
          urlParams.delete(param);
          values.forEach(value => {
            urlParams.append(this.layerURLParamName, value);
          });
        }
      });
      let newURL = window.location.pathname
      if(urlParams.size > 0)
        newURL = newURL + '?' + urlParams.toString() + window.location.hash;
      window.history.replaceState({}, '', newURL);
    }

    onRemove() {

    }

    togglePanel(e) {
      const action = e.target.dataset.action;
      const opening = (action === 'open');
      // set aria attributes
      this.$sidePanelContent.setAttribute('aria-hidden', !opening);
      this.$sidePanelContent.setAttribute('open', opening);
      if (opening) {
        this._container.classList.remove('dl-map__side-panel--collapsed');
        this.$openBtn.classList.add('js-hidden');
        this.$closeBtn.classList.remove('js-hidden');
        // focus on the panel when opening
        this._container.focus();
      } else {
        this._container.classList.add('dl-map__side-panel--collapsed');
        this.$openBtn.classList.remove('js-hidden');
        this.$closeBtn.classList.add('js-hidden');
        // focus on open btn when closing panel
        this.$openBtn.focus();
      }
    };

    // toggles visibility of elements/entities based on URL params
    toggleLayersBasedOnUrl() {
      const enabledLayers = this.getEnabledLayersFromUrl();
      this.showEntitiesForLayers(enabledLayers);
    };

    getEnabledLayersFromUrl() {
      // Get the URL parameters
      const urlParams = (new URL(document.location)).searchParams;

      // Get the names of the enabled and disabled layers
      // Only care about layers that exist
      let enabledLayerNames = [];
      if (urlParams.has(this.layerURLParamName)) {
          enabledLayerNames = urlParams
            .getAll(this.layerURLParamName)
            .filter(name => this.layerOptions.find((option) => option.getDatasetName() == name) != undefined)
            .map(name => this.layerOptions.find((option) => option.getDatasetName() == name));
      }

      return enabledLayerNames;
    }

    showEntitiesForLayers(enabledLayers) {

      const layerOptionsClone = [].concat(this.layerOptions);
      const disabledLayers = layerOptionsClone.filter(layer => enabledLayers.indexOf(layer) === -1);

      // pass correct this arg
      enabledLayers.forEach(layer => layer.enable());
      disabledLayers.forEach(layer => layer.disable());
    }

    enabledLayers() {
      return this.layerOptions.filter(option => option.isChecked())
    };

    filterCheckboxes(e) {
      var query = e.target.value;
      var filteredCheckboxes = this.filterCheckboxesArr(query);
      this.displayMatchingCheckboxes(filteredCheckboxes)
    };

    filterCheckboxesArr(query) {
      return this.layerOptions.filter(layerOption => layerOption.getDatasetName().toLowerCase().indexOf(query.toLowerCase()) !== -1)
    };

    displayMatchingCheckboxes(layerOptions, cb) {
      // hide all
      this.layerOptions.forEach(layerOption => layerOption.setLayerCheckboxVisibility(false));
      // re show those in filtered array
      layerOptions.forEach(layerOption => layerOption.setLayerCheckboxVisibility(true));
      if (cb) {
        cb();
      }
    };

    updateUrl() {
      // set the url params based on the enabled layers
      const urlParams = (new URL(document.location)).searchParams;
      urlParams.delete(this.layerURLParamName);

      this.enabledLayers().forEach((layer) =>
        urlParams.append(this.layerURLParamName, layer.getDatasetName())
      );

      let newURL =
        window.location.pathname +
        "?" +
        urlParams.toString() +
        window.location.hash;

      // add entry to history, does not fire event so need to call toggleLayersBasedOnUrl
      window.history.pushState({}, '', newURL);
      this.toggleLayersBasedOnUrl();
    }

    getClickableLayers() {
      var clickableLayers = [];
      var enabledLayers = this.enabledLayers().map(layer => layer.getDatasetName());

      return enabledLayers.map((layer) => {
        var components = this.availableLayers[layer];

        if (components.includes(layer + 'Fill')) {
          return layer + 'Fill';
        }

        return components[0];
      });
    }
}

export class LayerOption {
  constructor(layer, availableLayers, layerControls){
    this.layer = layer;
    this.element = this.makeElement(layer);
    this.layerControls = layerControls;
    this.availableLayers = availableLayers;
  }

  makeElement(layer) {
    const listItem = document.createElement('li');
    listItem.classList.add("dl-map__layer-item");
    listItem.classList.add("govuk-!-margin-bottom-1");

    const checkBoxDiv = document.createElement('div');
    checkBoxDiv.classList.add("govuk-checkboxes__item");

    const checkBoxInput = document.createElement('input');
    checkBoxInput.classList.add("govuk-checkboxes__input");
    checkBoxInput.setAttribute('id', layer.dataset);
    checkBoxInput.setAttribute('name', layer.dataset);
    checkBoxInput.setAttribute('type', 'checkbox');
    checkBoxInput.setAttribute('value', layer.dataset);
    checkBoxInput.addEventListener('change', this.clickHandler.bind(this));

    const checkBoxLabel = document.createElement('label');
    checkBoxLabel.classList.add("govuk-label");
    checkBoxLabel.classList.add("govuk-checkboxes__label");
    checkBoxLabel.setAttribute('for', layer.dataset);
    checkBoxLabel.innerHTML = this.makeLayerSymbol(layer);

    checkBoxDiv.appendChild(checkBoxInput);
    checkBoxDiv.appendChild(checkBoxLabel);
    listItem.appendChild(checkBoxDiv);

    return listItem;
  }

  makeLayerSymbol(layer) {
    let symbolHtml = '';

    let opacityNumber = (layer.paint_options && layer.paint_options.opacity) ? layer.paint_options.opacity : defaultPaintOptions["fill-opacity"];
    let color = (layer.paint_options && layer.paint_options.colour) ? layer.paint_options.colour : defaultPaintOptions["fill-color"];

    if(layer.paint_options && layer.paint_options.type && layer.paint_options.type == 'point') {
      const fill =
      symbolHtml = `
        <svg class="dl-label__key__symbol--pin" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xml:space="preserve" viewBox="0 0 90 90">
          <defs>
          </defs>
          <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10;" >
            <path
              d="M 45 0 C 27.677 0 13.584 14.093 13.584 31.416 c 0 4.818 1.063 9.442 3.175 13.773 c 2.905 5.831 11.409 20.208 20.412 35.428 l 4.385 7.417 C 42.275 89.252 43.585 90 45 90 s 2.725 -0.748 3.444 -1.966 l 4.382 -7.413 c 8.942 -15.116 17.392 -29.4 20.353 -35.309 c 0.027 -0.051 0.055 -0.103 0.08 -0.155 c 2.095 -4.303 3.157 -8.926 3.157 -13.741 C 76.416 14.093 62.323 0 45 0 z M 45 42.81 c -6.892 0 -12.5 -5.607 -12.5 -12.5 c 0 -6.893 5.608 -12.5 12.5 -12.5 c 6.892 0 12.5 5.608 12.5 12.5 C 57.5 37.202 51.892 42.81 45 42.81 z"
              style="
                stroke: none;
                stroke-width: 1;
                stroke-dasharray: none;
                stroke-linecap: butt;
                stroke-linejoin: miter;
                stroke-miterlimit: 10;
                fill: ${color};
                fill-rule: nonzero;
                opacity: ${opacityNumber};"
                transform=" matrix(1 0 0 1 0 0) "
                stroke-linecap="round"
              />
          </g>
        </svg>`
    } else {



      const opacity = parseInt((opacityNumber * 255)).toString(16);
      symbolHtml = `
        <span
          class="dl-label__key__symbol"
          style="
            border-color: ${color};
            background: ${color}${opacity};
          "
        >
        </span>
      `
    }

    const html = `<span class="dl-label__key">${symbolHtml}${layer.name}</span>`;
    return html;
  }

  clickHandler(e) {
    this.layerControls.updateUrl();
  }

  enable() {
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = true;
    this.element.dataset.layerControlActive = 'true';
    this.element.classList.remove(this.layerControlDeactivatedClass);
    this.setLayerVisibility(true);
  };

  disable() {
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = false;
    this.element.dataset.layerControlActive = 'false';
    this.element.classList.add(this.layerControlDeactivatedClass);
    this.setLayerVisibility(false);
  };

  isChecked(){
    return this.element.querySelector('input[type="checkbox"]').checked
  }

  setLayerVisibility(visible) {
    const visibility = (visible) ? 'visible' : 'none';
    this.availableLayers.forEach(layerId => this.layerControls.mapController.setLayerVisibility(layerId, visibility));
  }

  setLayerCheckboxVisibility(display) {
    const displayString = display ? 'block' : 'none';
    this.element.style.display = displayString;
  }

  getDatasetName(){
    return this.layer.dataset;
  }
}
