var MOJFrontend = {};

MOJFrontend.SortableTable = function(params) {
  this.table = $(params.table);
  this.setupOptions(params);
  this.body = this.table.find("tbody");
  this.createHeadingButtons();
  this.createStatusBox();
  this.table.on("click", "th button", $.proxy(this, "onSortButtonClick"));
};

MOJFrontend.SortableTable.prototype.setupOptions = function(params) {
  params = params || {};
  this.statusMessage =
    params.statusMessage || "Sorted by %heading% (%direction%)";
  this.ascendingText = params.ascendingText || "ascending";
  this.descendingText = params.descendingText || "descending";
  this.statusVisible = params.statusVisible || false;
  this.tableWrapper = params.tableWrapperSelector
    ? this.table.closest(params.tableWrapperSelector)
    : this.table.parent();
};

MOJFrontend.SortableTable.prototype.createHeadingButtons = function() {
  var headings = this.table.find("thead th");
  var heading;
  for (var i = 0; i < headings.length; i++) {
    heading = $(headings[i]);
    if (heading.attr("aria-sort")) {
      this.createHeadingButton(heading, i);
    }
  }
};

MOJFrontend.SortableTable.prototype.createHeadingButton = function(heading, i) {
  var text = heading.text();
  var button = $(
    '<button type="button" data-index="' + i + '">' + text + "</button>"
  );
  heading.text("");
  heading.append(button);
};

MOJFrontend.SortableTable.prototype.createStatusBox = function() {
  var classes = this.statusVisible
    ? "sortable-table__status"
    : "govuk-visually-hidden";
  this.status = $(
    '<div aria-live="polite" role="status" aria-atomic="true" />'
  ).addClass(classes);
  this.tableWrapper.prepend(this.status);
};

MOJFrontend.SortableTable.prototype.onSortButtonClick = function(e) {
  var columnNumber = e.currentTarget.getAttribute("data-index");
  var sortDirection = $(e.currentTarget)
    .parent()
    .attr("aria-sort");
  var newSortDirection;
  if (sortDirection === "none" || sortDirection === "descending") {
    newSortDirection = "ascending";
  } else {
    newSortDirection = "descending";
  }
  var rows = this.getTableRowsArray();
  var sortedRows = this.sort(rows, columnNumber, newSortDirection);
  this.addRows(sortedRows);
  this.removeButtonStates();
  this.updateButtonState($(e.currentTarget), newSortDirection);
};

MOJFrontend.SortableTable.prototype.updateButtonState = function(
  button,
  direction
) {
  button.parent().attr("aria-sort", direction);
  var message = this.statusMessage;
  message = message.replace(/%heading%/, button.text());
  message = message.replace(/%direction%/, this[direction + "Text"]);
  this.status.text(message);
  this.tableWrapper.addClass("table-sort--active");
};

MOJFrontend.SortableTable.prototype.removeButtonStates = function() {
  this.table.find("thead th").attr("aria-sort", "none");
};

MOJFrontend.SortableTable.prototype.addRows = function(rows) {
  for (var i = 0; i < rows.length; i++) {
    this.body.append(rows[i]);
  }
};

MOJFrontend.SortableTable.prototype.getTableRowsArray = function() {
  var rows = [];
  var trs = this.body.find("tr");
  for (var i = 0; i < trs.length; i++) {
    rows.push(trs[i]);
  }
  return rows;
};

MOJFrontend.SortableTable.prototype.sort = function(
  rows,
  columnNumber,
  sortDirection
) {
  var newRows = rows.sort(
    $.proxy(function(rowA, rowB) {
      var tdA = $(rowA)
        .find("td")
        .eq(columnNumber);
      var tdB = $(rowB)
        .find("td")
        .eq(columnNumber);
      var valueA = this.getCellValue(tdA);
      var valueB = this.getCellValue(tdB);
      if (sortDirection === "ascending") {
        if (valueA < valueB) {
          return -1;
        }
        if (valueA > valueB) {
          return 1;
        }
        return 0;
      } else {
        if (valueB < valueA) {
          return -1;
        }
        if (valueB > valueA) {
          return 1;
        }
        return 0;
      }
    }, this)
  );
  return newRows;
};

MOJFrontend.SortableTable.prototype.getCellValue = function(cell) {
  var val = cell.attr("data-sort-value");
  val = val || cell.html();
  // isNumeric is deprecated. So using native isNaN
  if (!isNaN(val)) {
    // keep floats as floats. +val casts to number
    return +val;
  }
  return val;
};
