// so_well/static/js/modules/streetTypeOptions.js
export function fetchStreetTypeOptions() {
    $.ajax({
        url: '/advanced_search/street_types',
        method: 'GET',
        success: function(data) {
            data.street_types.forEach(function(streetType) {
                $('#street-type-options').append(`<div><input type="checkbox" class="street-type-option" value="${streetType.value}"> ${streetType.value}</div>`);
            });
        }
    });
}
