export default class FilterCheckboxesController{
    constructor(checkboxContainer, searchBox){
        this.checkboxContainer = checkboxContainer;

        // get the checkboxes, and checkbox values
        // make sure we are working with an array and not a node list
        this.checkboxes = Array.prototype.slice.call(this.checkboxContainer.children) ;
        this.checkboxStrings = [];
        this.checkboxes.forEach(checkbox => {
            let datasetName = checkbox.querySelector('.govuk-checkboxes__input').value;

            this.checkboxStrings.push(datasetName);
        })

        // get the search box
        this.searchBox = searchBox;
        this.searchBox.addEventListener('keyup', this.filterCheckboxes.bind(this));

        // call filter checkboxes to set the initial state
        this.filterCheckboxes();
    }

    filterCheckboxes(){
        let searchValue = this.searchBox.value.toLowerCase();
        this.checkboxStrings.forEach((checkboxString, index) => {
            if(checkboxString.toLowerCase().indexOf(searchValue) > -1){
                this.checkboxes[index].style.display = "block";
            } else {
                this.checkboxes[index].style.display = "none";
            }
        })
    }


}
