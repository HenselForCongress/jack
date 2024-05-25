// so_well/static/js/modules/stateOptions.js
export function fetchStateOptions() {
    $.ajax({
        url: '/advanced_search/states',
        method: 'GET',
        success: function(data) {
            data.forEach(function(state) {
                $('#state').append(`<option value="${state}">${state}</option>`);
            });
        }
    });
}
