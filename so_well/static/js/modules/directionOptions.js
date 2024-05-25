// so_well/static/js/modules/directionOptions.js
export function fetchDirectionOptions() {
    $.ajax({
        url: '/advanced_search/directions',
        method: 'GET',
        success: function(data) {
            data.directions.forEach(function(direction) {
                $('#direction-options').append(`<div><input type="checkbox" class="direction-option" value="${direction.value}"> ${direction.value}</div>`);
            });

            data.post_directions.forEach(function(postDirection) {
                $('#post-direction-options').append(`<div><input type="checkbox" class="post-direction-option" value="${postDirection.value}"> ${postDirection.value}</div>`);
            });
        }
    });
}
