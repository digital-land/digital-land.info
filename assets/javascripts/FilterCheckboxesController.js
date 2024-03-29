export default class FilterCheckboxesController{
    constructor(id){
        this.checkboxContainer = document.getElementById(`checkboxes-${id}`);
        this.searchBox = document.getElementById(`input-${id}`);
        this.searchBoxContainer = document.getElementById(`input-container-${id}`);

        this.searchBoxContainer.style.display = "block";

        // get the checkboxes, and checkbox values
        // make sure we are working with an array and not a node list
        this.checkboxes = Array.prototype.slice.call(this.checkboxContainer.children) ;
        this.checkboxStrings = [];
        this.checkboxes.forEach(checkbox => {
            let datasetName = checkbox.querySelector('.govuk-checkboxes__label').innerHTML;

            this.checkboxStrings.push(datasetName);
        })

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
