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

        // Prepare data for the signature chart
        let signatureLabels = Object.keys(stats);
        let signatureData = Object.values(stats);
        let signatureBackgroundColors = ['#007bff', '#28a745', '#dc3545', '#ffc107'];

        // Create or update the signature chart
        let signatureCtx = document.getElementById('signatureChart').getContext('2d');
        new Chart(signatureCtx, {
            type: 'doughnut',
            data: {
                labels: signatureLabels,
                datasets: [{
                    data: signatureData,
                    backgroundColor: signatureBackgroundColors
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

        // Example data for sheet status chart (replace with real data as needed)
        let statusLabels = ['Printed', 'Signing', 'Summarizing', 'Closed', 'Pre-shipment', 'Shipped', 'Submission', 'Complete'];
        let statusData = [191, 12, 8, 0, 0, 0, 7, 2]; // Example values
        let statusBackgroundColors = ['#6c757d', '#17a2b8', '#ffc107', '#28a745', '#fd7e14', '#dc3545', '#007bff', '#6f42c1'];

        // Create or update the sheet status chart
        let statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {
            type: 'bar',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: statusBackgroundColors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                let label = tooltipItem.label || '';
                                let value = tooltipItem.raw;
                                return `${label}: ${value}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Status'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
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
