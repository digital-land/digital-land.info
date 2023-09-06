export default class BrandImageControl {
	constructor(options = {}) {
        if(!options.imageSrc){
            throw new Error('BrandImageControl requires an imageSrc option');
        }

        this.imageSrc = options.imageSrc;

		this._container = document.createElement('div');
		const styleClasses = this._container.classList;
		styleClasses.add('maplibregl-ctrl');
	}

	onAdd(map) {
		const image = document.createElement('img');
        image.src = this.imageSrc;

        this._container.appendChild(image);
		return this._container;
	}

	onRemove() {

	}
}
