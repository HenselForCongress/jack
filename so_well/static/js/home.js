// so_well/static/js/home.js
$(document).ready(function() {
    // Fetch and display statistics
    fetchStatistics();

    function fetchStatistics() {
        $.ajax({
            url: '/signatures/stats',
            method: 'GET',
            success: function(data) {
                console.log('Statistics data:', data);
                displayStatistics(data);
            },
            error: function(xhr, status, error) {
                console.error('Error fetching statistics:', error);
            }
        });
    }

    function displayStatistics(stats) {
        // Get total signatures
        let totalSignatures = Object.values(stats).reduce((a, b) => a + b, 0);

        // Prepare data for the chart
        let labels = Object.keys(stats);
        let data = Object.values(stats);
        let backgroundColors = ['#007bff', '#28a745', '#dc3545', '#ffc107'];

        // Create or update the chart
        let ctx = document.getElementById('signatureChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                let label = tooltipItem.label || '';
                                let value = tooltipItem.raw;
                                let percentage = ((value / totalSignatures) * 100).toFixed(2);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        // Update progress bar
        let matchedSignatures = stats['Matched'] || 0;
        let progress = Math.min((matchedSignatures / 1000) * 100, 100).toFixed(2);
        $('#progress-bar').css('width', progress + '%').text(`${progress}%`);
    }
});
