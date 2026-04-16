import {defaultPaintOptions} from "./defaultPaintOptions.js";

export default class LayerControls {
    constructor (mapController, source, layers, availableLayers, options) {
      this.mapController = mapController;
      this.tileSource = source;
      this.layers = layers;
      this.availableLayers = availableLayers;
      this.options = options;

      this._container = document.createElement('div');
      this.layerOptions = [];
      this.dataQualityOptions = [];

		  const styleClasses = this._container.classList;
      styleClasses.add('maplibregl-ctrl')

      this.layerURLParamName = options.layerURLParamName || 'dataset';
      this.redirectURLParamNames = options.redirectURLParamNames || [];
      this.enableTabs = options.enableTabs || false;
      this.dataQualityLayers = options.dataQualityLayers || [];
      this.dataQualityInfo = options.dataQualityInfo || [];

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

      // Create content div to include search input, and dataset checkboxes
      const content = document.createElement('div');
      content.classList.add('dl-map__side-panel__content');
      this.$sidePanelContent = content;

      // Create footer div to include quality description
      const footer = document.createElement('div');
      footer.classList.add('dl-map__side-panel__footer');
      footer.style.display = 'none'; // Initially hidden
      this.$sidePanelFooter = footer;

      // Create Data layers panel
      const dataLayersPanel = document.createElement('div');
      let dataQualityPanel = null;

      if (this.enableTabs) {
        // Create GOV.UK tabs structure
        const tabsContainer = document.createElement('div');
        tabsContainer.classList.add('govuk-tabs');
        tabsContainer.setAttribute('data-module', 'govuk-tabs');

        // Create tab list
        const tabList = document.createElement('ul');
        tabList.classList.add('govuk-tabs__list');
        tabList.setAttribute('role', 'tablist');

        // Data layers tab
        const dataLayersTabItem = document.createElement('li');
        dataLayersTabItem.classList.add('govuk-tabs__list-item', 'govuk-tabs__list-item--selected');

        const dataLayersTab = document.createElement('a');
        dataLayersTab.classList.add('govuk-tabs__tab');
        dataLayersTab.href = '#data-layers';
        dataLayersTab.setAttribute('role', 'tab');
        dataLayersTab.setAttribute('aria-selected', 'true');
        dataLayersTab.setAttribute('aria-controls', 'data-layers');
        dataLayersTab.textContent = 'Data layers';

        dataLayersTabItem.appendChild(dataLayersTab);
        tabList.appendChild(dataLayersTabItem);

        // Always create data quality tab
        const dataQualityTabItem = document.createElement('li');
        dataQualityTabItem.classList.add('govuk-tabs__list-item');

        const dataQualityTab = document.createElement('a');
        dataQualityTab.classList.add('govuk-tabs__tab');
        dataQualityTab.href = '#data-quality';
        dataQualityTab.setAttribute('role', 'tab');
        dataQualityTab.setAttribute('aria-selected', 'false');
        dataQualityTab.setAttribute('aria-controls', 'data-quality');
        dataQualityTab.textContent = 'Data quality';

        dataQualityTabItem.appendChild(dataQualityTab);
        tabList.appendChild(dataQualityTabItem);

        // Store tab references
        this.dataQualityTabItem = dataQualityTabItem;
        this.dataQualityTab = dataQualityTab;

        // Add tab click handler
        dataQualityTab.addEventListener('click', (e) => {
          e.preventDefault();
          this.switchTab('data-quality');
        });

        tabsContainer.appendChild(tabList);
        heading.appendChild(tabsContainer);

        // Store tab references
        this.dataLayersTabItem = dataLayersTabItem;
        this.dataLayersTab = dataLayersTab;

        // Add tab click handler
        dataLayersTab.addEventListener('click', (e) => {
          e.preventDefault();
          this.switchTab('data-layers');
        });

        // Create and configure panel elements while we're in the tabs block
        dataLayersPanel.classList.add('govuk-tabs__panel');
        dataLayersPanel.setAttribute('id', 'data-layers');
        dataLayersPanel.setAttribute('role', 'tabpanel');
        dataLayersPanel.setAttribute('aria-labelledby', 'data-layers');

        dataQualityPanel = document.createElement('div');
        dataQualityPanel.classList.add('govuk-tabs__panel', 'govuk-tabs__panel--hidden');
        dataQualityPanel.setAttribute('id', 'data-quality');
        dataQualityPanel.setAttribute('role', 'tabpanel');
        dataQualityPanel.setAttribute('aria-labelledby', 'data-quality');
      }

      sidePanel.appendChild(heading);

      this.$textbox = document.createElement('input');
      this.$textbox.setAttribute('id', 'input-71108');
      this.$textbox.classList.add('govuk-input', 'dl-filter-group__auto-filter__input');
      this.$textbox.setAttribute('type', 'text');
      this.$textbox.setAttribute('aria-describedby', 'checkbox-filter-71108');
      this.$textbox.setAttribute('aria-controls', 'checkboxes-71108');
      this.$textbox.addEventListener('input', this.filterCheckboxes.bind(this));

      // Create filter group for data layers
      const dataLayersFilterGroup = document.createElement('div');
      dataLayersFilterGroup.classList.add('dl-filter-group__auto-filter');

      const dataLayersFilterLabel = document.createElement('label');
      dataLayersFilterLabel.setAttribute('for', 'input-71108');
      dataLayersFilterLabel.classList.add('govuk-label', 'govuk-visually-hidden');
      dataLayersFilterLabel.textContent = 'Filter Show only';
      dataLayersFilterGroup.appendChild(dataLayersFilterLabel);
      dataLayersFilterGroup.appendChild(this.$textbox);

      // Create separate filter group for data quality tab
      let dataQualityFilterGroup = null;
      let dataQualityTextbox = null;

      if (this.enableTabs && dataQualityPanel) {
        dataQualityTextbox = document.createElement('input');
        dataQualityTextbox.setAttribute('id', 'input-quality-filter');
        dataQualityTextbox.classList.add('govuk-input', 'dl-filter-group__auto-filter__input');
        dataQualityTextbox.setAttribute('type', 'text');
        dataQualityTextbox.setAttribute('aria-describedby', 'quality-filter-desc');
        dataQualityTextbox.setAttribute('aria-controls', 'quality-radios');
        dataQualityTextbox.addEventListener('input', this.filterDataQualityOptions.bind(this));

        dataQualityFilterGroup = document.createElement('div');
        dataQualityFilterGroup.classList.add('dl-filter-group__auto-filter');

        const dataQualityFilterLabel = document.createElement('label');
        dataQualityFilterLabel.setAttribute('for', 'input-quality-filter');
        dataQualityFilterLabel.classList.add('govuk-label', 'govuk-visually-hidden');
        dataQualityFilterLabel.textContent = 'Filter data quality layers';
        dataQualityFilterGroup.appendChild(dataQualityFilterLabel);
        dataQualityFilterGroup.appendChild(dataQualityTextbox);

        this.$dataQualityTextbox = dataQualityTextbox;
      }

      // Create data quality controls
      const qualityRadios = document.createElement('div');
      qualityRadios.classList.add('govuk-radios');
      qualityRadios.setAttribute('data-module', `layer-controls-${this.mapController.mapId}}`);

      if (dataQualityFilterGroup) {
        qualityRadios.appendChild(dataQualityFilterGroup);
      }

      const qualityList = document.createElement('ul');
      qualityList.classList.add('govuk-list');
      qualityList.setAttribute('data-module', 'data-quality-toggles');
      qualityList.setAttribute('role', 'radiogroup');
      qualityList.setAttribute('id', 'quality-radios');

      // Create data quality options from the same data as layers
      this.dataQualityOptions = this.dataQualityLayers.map((layer) => {
        // Use source_dataset to get the correct available layers, fallback to layer.dataset
        const sourceDataset = layer.source_dataset || layer.dataset;
        return new DataQualityOption(layer, this.availableLayers[sourceDataset] || [], this);
      });

      this.dataQualityOptions.forEach(option => qualityList.appendChild(option.element));
      qualityRadios.appendChild(qualityList);

      // Create quality descriptions header and list in footer (initially hidden)
      const qualityDescriptionsHeader = document.createElement('div');
      qualityDescriptionsHeader.classList.add('govuk-!-margin-top-2', 'govuk-!-margin-left-2');
      const qualityDescriptionsHeaderSpan = document.createElement('span');
      qualityDescriptionsHeaderSpan.classList.add('govuk-heading-s');
      qualityDescriptionsHeaderSpan.textContent = 'Key:';
      qualityDescriptionsHeader.appendChild(qualityDescriptionsHeaderSpan);
      footer.appendChild(qualityDescriptionsHeader);

      const qualityDescriptions = document.createElement('ul');
      qualityDescriptions.classList.add('govuk-list');
      qualityDescriptions.setAttribute('id', 'quality-descriptions');
      footer.appendChild(qualityDescriptions);

      // Store reference to quality descriptions list and header
      this.qualityDescriptions = qualityDescriptions;
      this.qualityDescriptionsHeader = qualityDescriptionsHeader;

      if (dataQualityPanel) {
        dataQualityPanel.appendChild(qualityRadios);
      }

      // Store panel references
      this.dataLayersPanel = dataLayersPanel;
      this.dataQualityPanel = dataQualityPanel;

      const checkboxes = document.createElement('div');
      checkboxes.classList.add('govuk-checkboxes');
      checkboxes.setAttribute('data-module', `layer-controls-${this.mapController.mapId}}`);
      checkboxes.appendChild(dataLayersFilterGroup);

      const list = document.createElement('ul');
      list.classList.add('govuk-list');
      list.setAttribute('data-module', 'layer-toggles');
      list.setAttribute('role', 'group');

      this.layerOptions = this.layers.map((layer) => {
        return new LayerOption(layer, this.availableLayers[layer.dataset], this);
      });

      this.layerOptions.forEach(option => list.appendChild(option.element));

      checkboxes.appendChild(list);
      dataLayersPanel.appendChild(checkboxes);

      // Add panels to content
      content.appendChild(dataLayersPanel);
      if (dataQualityPanel) {
        content.appendChild(dataQualityPanel);
      }
      sidePanel.appendChild(content);
      sidePanel.appendChild(footer);

      this.$sidePanel = sidePanel;

      const boundTogglePanel = this.togglePanel.bind(this);
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

    togglePanel(e) {
      const action = e.target.dataset.action;
      const opening = (action === 'open');
      // set aria attributes
      this.$sidePanelContent.setAttribute('aria-hidden', !opening);
      this.$sidePanelContent.setAttribute('open', opening);
      if (opening) {
        this._container.classList.remove('dl-map__side-panel--collapsed');
        this.$openBtn.classList.add('js-hidden');
        // focus on the panel when opening
        this._container.focus();
      } else {
        this._container.classList.add('dl-map__side-panel--collapsed');
        this.$openBtn.classList.remove('js-hidden');
        // focus on open btn when closing panel
        this.$openBtn.focus();
      }
    };

    switchTab(tabId) {
      if (!this.enableTabs) return;

      // Update tab states
      if (tabId === 'data-layers') {

        // Activate data layers tab
        this.dataLayersTabItem.classList.add('govuk-tabs__list-item--selected');
        this.dataLayersTab.setAttribute('aria-selected', 'true');
        this.dataLayersPanel.classList.remove('govuk-tabs__panel--hidden');

        // Deactivate data quality tab
        this.dataQualityTabItem.classList.remove('govuk-tabs__list-item--selected');
        this.dataQualityTab.setAttribute('aria-selected', 'false');
        this.dataQualityPanel.classList.add('govuk-tabs__panel--hidden');

        // Clear search inputs and reset visibility
        this.$textbox.value = '';
        if (this.$dataQualityTextbox) {
          this.$dataQualityTextbox.value = '';
        }

        // Clear all selections
        this.layerOptions.forEach(option => option.disable());
        if (this.dataQualityOptions) {
          this.dataQualityOptions.forEach(option => option.disable());
        }

        // Hide and clear quality descriptions
        if (this.qualityDescriptions) {
          this.qualityDescriptions.innerHTML = '';
          this.$sidePanelFooter.style.display = 'none';
        }

        // Reset content height
        this.$sidePanelContent.classList.remove('dl-map__side-panel__content--with-footer');

        // Show all data layers
        this.displayMatchingCheckboxes(this.layerOptions);

        // Show all data quality options
        if (this.dataQualityOptions) {
          this.displayMatchingDataQualityOptions(this.dataQualityOptions);
        }

      } else if (tabId === 'data-quality') {

        // Activate data quality tab
        this.dataQualityTabItem.classList.add('govuk-tabs__list-item--selected');
        this.dataQualityTab.setAttribute('aria-selected', 'true');
        this.dataQualityPanel.classList.remove('govuk-tabs__panel--hidden');

        // Deactivate data layers tab
        this.dataLayersTabItem.classList.remove('govuk-tabs__list-item--selected');
        this.dataLayersTab.setAttribute('aria-selected', 'false');
        this.dataLayersPanel.classList.add('govuk-tabs__panel--hidden');

        // Clear search inputs and reset visibility
        this.$textbox.value = '';

        if (this.$dataQualityTextbox) {
          this.$dataQualityTextbox.value = '';
        }

        // Clear all selections
        this.layerOptions.forEach(option => option.disable());
        if (this.dataQualityOptions) {
          this.dataQualityOptions.forEach(option => option.disable());
        }

        // Hide and clear quality descriptions
        if (this.qualityDescriptions) {
          this.qualityDescriptions.innerHTML = '';
          this.$sidePanelFooter.style.display = 'none';
        }

        // Reset content height
        this.$sidePanelContent.classList.remove('dl-map__side-panel__content--with-footer');

        // Show all data layers
        this.displayMatchingCheckboxes(this.layerOptions);
        // Show all data quality options

        if (this.dataQualityOptions) {
          this.displayMatchingDataQualityOptions(this.dataQualityOptions);
        }
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

    enabledDataQualityLayers() {
      return this.dataQualityOptions.filter(option => option.isSelected())
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

    filterDataQualityOptions(e) {
      var query = e.target.value;
      var filteredOptions = this.filterDataQualityOptionsArr(query);
      this.displayMatchingDataQualityOptions(filteredOptions);
    };

    filterDataQualityOptionsArr(query) {
      return this.dataQualityOptions.filter(option => option.getDatasetName().toLowerCase().indexOf(query.toLowerCase()) !== -1);
    };

    displayMatchingDataQualityOptions(options, cb) {
      // hide all
      this.dataQualityOptions.forEach(option => option.setOptionVisibility(false));
      // re show those in filtered array
      options.forEach(option => option.setOptionVisibility(true));
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

      // Include enabled checkbox layers (Data layers tab)
      var enabledLayers = this.enabledLayers().map(layer => layer.getDatasetName());

      // Include enabled radio button layers (Data quality tab)
      // For data quality layers, use the source dataset to get the correct available layers
      var enabledDataQualityLayers = this.enabledDataQualityLayers().map(layer => {
        return layer.layer.source_dataset || layer.getDatasetName();
      });

      // Combine all enabled layers
      var allEnabledLayers = [...enabledLayers, ...enabledDataQualityLayers];

      return allEnabledLayers.map((layer) => {
        var components = this.availableLayers[layer];

        if (components && components.includes(layer + 'Fill')) {
          return layer + 'Fill';
        }

        return components ? components[0] : null;
      }).filter(layer => layer !== null);
    }
}

export class LayerOption {
  constructor(layer, availableLayers, layerControls){
    this.layer = layer;
    this.element = this.makeElement(layer);
    this.layerControls = layerControls;
    this.availableLayers = availableLayers;
    this.layerControlDeactivatedClass = 'dl-map__layer-item--deactivated';
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

export class DataQualityOption {
  constructor(layer, availableLayers, layerControls){
    this.layer = layer;
    this.element = this.makeElement(layer);
    this.layerControls = layerControls;
    this.availableLayers = availableLayers;
    this.layerControlDeactivatedClass = 'dl-map__layer-item--deactivated';
  }

  makeElement(layer) {
    const listItem = document.createElement('li');
    listItem.classList.add("dl-map__data-quality-item");
    listItem.classList.add("govuk-!-margin-bottom-1");
    listItem.setAttribute('data-layer-control', layer.dataset);
    listItem.setAttribute('data-layer-type', 'data-quality');

    const radioDiv = document.createElement('div');
    radioDiv.classList.add("govuk-radios__item");

    const radioInput = document.createElement('input');
    radioInput.classList.add("govuk-radios__input");
    radioInput.setAttribute('id', `data-quality-${layer.dataset}`);
    radioInput.setAttribute('name', 'data-quality-layers');
    radioInput.setAttribute('type', 'radio');
    radioInput.setAttribute('value', layer.dataset);
    radioInput.addEventListener('change', this.clickHandler.bind(this));

    const radioLabel = document.createElement('label');
    radioLabel.classList.add("govuk-label");
    radioLabel.classList.add("govuk-radios__label");
    radioLabel.setAttribute('for', `data-quality-${layer.dataset}`);

    // Create label content with just text (no colorful icons)
    radioLabel.textContent = layer.name;

    radioDiv.appendChild(radioInput);
    radioDiv.appendChild(radioLabel);
    listItem.appendChild(radioDiv);

    return listItem;
  }

  clickHandler(e) {
    // Deselect all other data quality options
    this.layerControls.dataQualityOptions.forEach(option => {
      if (option !== this) {
        option.disable();
      }
    });

    // Enable this option
    this.enable();

    // Show quality descriptions for this dataset
    this.showQualityDescriptions();
  }

  enable() {
    const $radio = this.element.querySelector('input[type="radio"]');
    $radio.checked = true;
    this.element.dataset.layerControlActive = 'true';
    this.element.classList.remove(this.layerControlDeactivatedClass);
    this.setLayerVisibility(true);
  }

  disable() {
    const $radio = this.element.querySelector('input[type="radio"]');
    $radio.checked = false;
    this.element.dataset.layerControlActive = 'false';
    this.element.classList.add(this.layerControlDeactivatedClass);
    this.setLayerVisibility(false);
  }

  isSelected() {
    return this.element.querySelector('input[type="radio"]').checked
  }

  setLayerVisibility(visible) {
    const visibility = (visible) ? 'visible' : 'none';
    this.availableLayers.forEach(layerId => this.layerControls.mapController.setLayerVisibility(layerId, visibility));
  }

  getDatasetName() {
    return this.layer.dataset;
  }

  setOptionVisibility(display) {
    const displayString = display ? 'block' : 'none';
    this.element.style.display = displayString;
  }

  showQualityDescriptions() {
    const qualityDescriptionsEl = this.layerControls.qualityDescriptions;
    const qualityDescriptionsHeader = this.layerControls.qualityDescriptionsHeader;
    const dataQualityInfo = this.layerControls.dataQualityInfo;
    const footer = this.layerControls.$sidePanelFooter;
    const content = this.layerControls.$sidePanelContent;

    if (!qualityDescriptionsEl || !dataQualityInfo || !footer) return;

    // Find quality descriptions for this dataset's source dataset
    const sourceDataset = this.layer.source_dataset || this.layer.dataset;
    const qualitiesForDataset = dataQualityInfo.filter(info =>
      info.source_dataset === sourceDataset
    );

    // Clear existing content
    qualityDescriptionsEl.innerHTML = '';

    if (qualitiesForDataset.length > 0) {

      // Add each quality description using the new colourbox structure
      qualitiesForDataset.forEach(qualityInfo => {
        const listItem = document.createElement('li');
        listItem.classList.add('govuk-!-margin-bottom-1');

        const colourboxDiv = document.createElement('div');
        colourboxDiv.classList.add('govuk-colourbox__item');

        const colourboxSpan = document.createElement('span');
        colourboxSpan.classList.add('govuk-colourbox__span');
        colourboxSpan.textContent = qualityInfo.description;

        // Set CSS custom properties for the color and opacity
        const color = qualityInfo.paint_options?.colour || '#003078';
        const opacity = qualityInfo.paint_options?.opacity || 0.7;
        colourboxSpan.style.setProperty('--quality-color', color);
        colourboxSpan.style.setProperty('--quality-opacity', opacity);

        colourboxDiv.appendChild(colourboxSpan);
        listItem.appendChild(colourboxDiv);
        qualityDescriptionsEl.appendChild(listItem);
      });

      // Show the footer, header and adjust content height
      qualityDescriptionsHeader.style.display = 'block';
      footer.style.display = 'block';
      content.classList.add('dl-map__side-panel__content--with-footer');
    } else {
      // Hide footer and reset content height
      qualityDescriptionsHeader.style.display = 'none';
      footer.style.display = 'none';
      content.classList.remove('dl-map__side-panel__content--with-footer');
    }
  }
}
