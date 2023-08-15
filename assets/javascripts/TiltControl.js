export default class TiltControl {
	constructor(options = {}) {
		this.tilted = false;

		this._container = document.createElement('div');

		const styleClasses = this._container.classList;

		styleClasses.add('maplibregl-ctrl');

		this._container.addEventListener('mouseenter', () => {
			styleClasses.add('maplibregl-ctrl-active');
		});

		this._container.addEventListener('mouseleave', () => {
			styleClasses.remove('maplibregl-ctrl-active');
		});
	}

	onAdd(map) {
		this._map = map;
		this.button = document.createElement('button');
		this.button.classList.add([
			'dl-map__tilt-toggle'
		]);
		this.button.textContent = '3D';
		this.button.addEventListener('click', this.clickHandler.bind(this));
		this._container.appendChild(this.button);

		this._map.on('pitch', this.tiltHandler.bind(this));

		return this._container;
	}

	onRemove() {
		this._container.parentNode.removeChild(this._container);
		this._map.removeEventListener('pitch', this.tiltHandler);
		this.button.removeEventListener('click', this.clickHandler);
		this._map = undefined;
	}

	tiltHandler(){
		this.tilted = this._map.getPitch() != 0;
		this.button.textContent = this.tilted ? '2D' : '3D';
	}

	clickHandler() {
		this._map.easeTo({
			pitch: this.tilted ? 0 : 45,
			duration: 200
		});
	}
}
