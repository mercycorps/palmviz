// Globally set the Bootstrap date-picker format.
$.fn.datepicker.defaults.format = "yyyy-mm-dd";

// sandbox env to play with:
// https://uxsolutions.github.io/bootstrap-datepicker/
$('.input-daterange').datepicker({
    todayHighlight: true
});