import {defaultPaintOptions} from "./defaultPaintOptions.js";

export default class LayerControls {
    constructor ($module, mapController, source, layers, availableLayers, options) {
      this.$module = $module;
      this.mapController = mapController;
      this.tileSource = source;
      this.layers = layers;
      this.availableLayers = availableLayers;

      this._container = document.createElement('div');
      this.layerOptions = [];

		  const styleClasses = this._container.classList;
      styleClasses.add('maplibregl-ctrl')

      this.layerURLParamName = options.layerURLParamName || 'layer';

      // listen for changes to URL
      var boundSetControls = this.toggleLayersBasedOnUrl.bind(this);
      window.addEventListener('popstate', function (event) {
        boundSetControls();
      });

      // initial set up of controls (default or urlParams)
      const urlParams = (new URL(document.location)).searchParams;
      if (!urlParams.has(this.layerURLParamName)) {
        // if not set then use default checked controls
        this.updateUrl();
      } else {
        // use URL params if available
        this.toggleLayersBasedOnUrl();
      }

      // this.init(options);
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

      const checkboxes = document.createElement('div');
      checkboxes.classList.add('govuk-checkboxes');
      checkboxes.setAttribute('data-module', 'layer-controls-{{ params.mapId if params.mapId else \'map\' }}');

      const filterGroup = document.createElement('div');
      filterGroup.classList.add('dl-filter-group__auto-filter');

      const filterLabel = document.createElement('label');
      filterLabel.setAttribute('for', 'input-71108');
      filterLabel.classList.add('govuk-label', 'govuk-visually-hidden');
      filterLabel.textContent = 'Filter Show only';

      const filterInput = document.createElement('input');
      filterInput.setAttribute('id', 'input-71108');
      filterInput.classList.add('govuk-input', 'dl-filter-group__auto-filter__input');
      filterInput.setAttribute('type', 'text');
      filterInput.setAttribute('aria-describedby', 'checkbox-filter-71108');
      filterInput.setAttribute('aria-controls', 'checkboxes-71108');

      filterGroup.appendChild(filterLabel);
      filterGroup.appendChild(filterInput);
      checkboxes.appendChild(filterGroup);

      const list = document.createElement('ul');
      list.classList.add('govuk-list', 'govuk-!-margin-bottom-0');
      list.setAttribute('data-module', 'layer-toggles');
      list.setAttribute('role', 'group');



      this.layerOptions = this.layers.map((layer) => {
        return new LayerOption(layer, this.availableLayers[layer.dataset], this);
      });

      this.layerOptions.forEach(option => list.appendChild(option.element));

      checkboxes.appendChild(list);
      content.appendChild(checkboxes);
      sidePanel.appendChild(content);

      this._container.appendChild(sidePanel);

      return this._container;
    }

    onRemove() {

    }

    init(params) {
      this.setupOptions(params);

      // add buttons to open and close panel
      this.$closeBtn = this.createCloseButton();
      this.$openBtn = this.createOpenButton();

      // find the search box
      this.$textbox = this.$module.querySelector('.dl-filter-group__auto-filter__input');
      this.$textbox.addEventListener('input', this.filterCheckboxes.bind(this));

      // get the aria description element
      this.ariaDescription = this.$module.querySelector('.dl-filter-group__auto-filter__desc');

      return this
    };

    setupOptions(params) {
      params = params || {};
      this.layerControlDeactivatedClass = params.layerControlDeactivatedClass || 'deactivated-control';
      this.layerURLParamName = params.layerURLParamName || 'layer';
      this.listItemSelector = params.listItemSelector || '.govuk-checkboxes__item';
    };

    createCloseButton() {
      const button = document.createElement('button');
      button.classList.add('dl-map__close-btn');
      button.dataset.action = 'close';
      const label = document.createElement('span');
      label.textContent = 'Close layer panel';
      label.classList.add('govuk-visually-hidden');
      button.appendChild(label);
      this.$container.appendChild(button);

      const boundTogglePanel = this.togglePanel.bind(this);
      button.addEventListener('click', boundTogglePanel);
      return button
    };

    createOpenButton() {
      const button = document.createElement('button');
      button.classList.add('dl-map__open-btn', 'dl-map__overlay', 'js-hidden');
      button.dataset.action = 'open';
      const label = document.createElement('span');
      label.textContent = 'Open layer panel';
      label.classList.add('govuk-visually-hidden');
      button.appendChild(label);
      this.mapController.map.getContainer().appendChild(button);

      const boundTogglePanel = this.togglePanel.bind(this);
      button.addEventListener('click', boundTogglePanel);
      return button
    };

    togglePanel(e) {
      const action = e.target.dataset.action;
      const opening = (action === 'open');
      // set aria attributes
      this.$container.setAttribute('aria-hidden', !opening);
      this.$container.setAttribute('open', opening);
      if (opening) {
        this.$container.classList.remove('dl-map__side-panel--collapsed');
        this.$openBtn.classList.add('js-hidden');
        // focus on the panel when opening
        this.$container.focus();
      } else {
        this.$container.classList.add('dl-map__side-panel--collapsed');
        this.$openBtn.classList.remove('js-hidden');
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
            .filter(name => this.layerOptions.find((option) => option.layer.dataset == name) != undefined)
            .map(name => this.layerOptions.find((option) => option.layer.dataset == name));
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

    updateUrl() {
      // set the url params based on the enabled layers
      const urlParams = (new URL(document.location)).searchParams;
      const enabledLayers = this.enabledLayers();
      urlParams.delete(this.layerURLParamName);
      enabledLayers.forEach(layer => urlParams.append(this.layerURLParamName, layer.getDatasetName()));
      const newURL = window.location.pathname + '?' + urlParams.toString() + window.location.hash;

      // add entry to history, does not fire event so need to call toggleLayersBasedOnUrl
      window.history.pushState({}, '', newURL);
      this.toggleLayersBasedOnUrl();
    };

    enabledLayers() {
      return this.layerOptions.filter(option => option.element.querySelector('input[type="checkbox"]').checked)
    };

    disabledLayers() {
      return this.$controls.filter($control => !option.element.querySelector('input[type="checkbox"]').checked)
    };

    getControlByName(dataset) {
      for (let i = 0; i < this.$controls.length; i++) {
        const $control = this.$controls[i];
        if ($control.dataset.layerControl === dataset) {
          return $control
        }
      }
      return undefined
    };

    onControlChkbxChange = function (e) {
      // when a control is changed update the URL params
      this.updateUrl();
    };

    getClickableLayers() {
      var clickableLayers = [];
      var enabledLayers = this.enabledLayers().map(layer => layer.getDatasetName());

      var clickableLayers = enabledLayers.map((layer) => {
        var components = this.availableLayers[layer];

        if (components.includes(layer + 'Fill')) {
          return layer + 'Fill';
        }

        return components[0];
      });

      return clickableLayers;
    }

    filterCheckboxes(e) {
      // get the value of the search box
      // get an array of filtered controls based on the value
      // render those controls to the layer control panel

      var query = e.target.value;
      var filteredCheckboxes = this.filterCheckboxesArr(query);
      this.displayMatchingCheckboxes(filteredCheckboxes)
    };

    filterCheckboxesArr(query) {
      var checkboxArr = this.checkboxArr;
      return checkboxArr.filter((el) => {
        const checkbox = el.querySelector('label');
        return checkbox.textContent.toLowerCase().indexOf(query.toLowerCase()) !== -1
      })
    };

    displayMatchingCheckboxes(checkboxArray, cb) {
      // hide all
      this.checkboxArr.forEach((checkBox) => {checkBox.style.display = 'none';});
      // re show those in filtered array
      checkboxArray.forEach((checkBox) => {checkBox.style.display = 'block';});

      if (cb) {
        cb();
      }
    };

    updateUrl() {
      // set the url params based on the enabled layers
      const urlParams = (new URL(document.location)).searchParams;
      urlParams.delete(this.layerURLParamName);

      this.enabledLayers().forEach(layer => urlParams.append(this.layerURLParamName, layer.getDatasetName()));
      const newURL = window.location.pathname + '?' + urlParams.toString() + window.location.hash;

      // add entry to history, does not fire event so need to call toggleLayersBasedOnUrl
      window.history.pushState({}, '', newURL);
      this.toggleLayersBasedOnUrl();
    }
}

class LayerOption {
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
    checkBoxInput.setAttribute('checked', 'checked');
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

    if(layer.paint_options.type && layer.paint_options.type == 'point') {
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
                fill:${layer.paint_options.colour||defaultPaintOptions["fill-color"]};
                fill-rule: nonzero;
                opacity: ${layer.paint_options.opacity||defaultPaintOptions["fill-opacity"]};"
                transform=" matrix(1 0 0 1 0 0) "
                stroke-linecap="round"
              />
          </g>
        </svg>`
    } else {
      layer.paint_options.opacity = layer.paint_options.opacity || 0.5;
      const opacity = parseInt((layer.paint_options.opacity * 255)).toString(16);
      symbolHtml = `
        <span
          class="dl-label__key__symbol"
          style="
            border-color: ${layer.paint_options.colour || '#003078'};
            background: ${(layer.paint_options.colour || '#003078')}${opacity};
          "
        >
        </span>
      `
    }

    const html = `<span class="dl-label__key">${symbolHtml}${layer.dataset}</span>`;
    return html;
  }

  clickHandler() {
    this.layerControls.updateUrl();
  }

  enable() {
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = true;
    this.element.dataset.layerControlActive = 'true';
    this.element.classList.remove(this.layerControlDeactivatedClass);
    this.toggleLayerVisibility(true);
  };

  disable() {
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = false;
    this.element.dataset.layerControlActive = 'false';
    this.element.classList.add(this.layerControlDeactivatedClass);
    this.toggleLayerVisibility(false);
  };

  toggleLayerVisibility(toEnable) {
    const visibility = (toEnable) ? 'visible' : 'none';
    this.availableLayers.forEach(layerId => this.layerControls.mapController.setLayerVisibility(layerId, visibility));
  }

  getDatasetName(){
    return this.layer.dataset;
  }
}
