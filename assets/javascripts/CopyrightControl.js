export default class CopyrightControl {
	constructor(options = {}) {
		this._container = document.createElement('div');
		const styleClasses = this._container.classList;
        styleClasses.add('copy-right-control');
	}

	onAdd(map) {
        this._container.innerHTML = `Contains OS data &copy; Crown copyright and database rights ${new Date().getFullYear()}`;
		return this._container;
	}

	onRemove() {

	}
}
