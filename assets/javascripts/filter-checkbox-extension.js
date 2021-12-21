function extendFilterCheckboxes($hiddenCount) {
    const originalGenerateAriaMessage = window.DLFrontend.FilterCheckboxes.prototype.generateAriaMessage
    //const $fgStatusUpdate = $controlsList.querySelector('.app-filter-group__status-update')
    $hiddenCount.classList.remove("js-hidden")

    function hideVisuallyIfZero($el, count) {
        if (count === 0) {
            $el.classList.add("govuk-visually-hidden")
        } else {
            $el.classList.remove("govuk-visually-hidden")
        }
    }

    // optionCount is the number still showing
    window.DLFrontend.FilterCheckboxes.prototype.generateAriaMessage = function (optionCount, selectedCount) {
        originalGenerateAriaMessage.call(this, optionCount, selectedCount)

        const hiddenCount = (optionCount > 0) ? this.checkboxArr.length - optionCount : 0;
        let text = hiddenCount.toString() + " "
        if (hiddenCount === 1) {
            text = text + $hiddenCount.dataset.single
        } else {
            text = text + $hiddenCount.dataset.multiple
        }

        text = text + " hidden"
        $hiddenCount.textContent = text
        hideVisuallyIfZero($hiddenCount, hiddenCount)
    }
}

window.extendFilterCheckboxes = extendFilterCheckboxes
