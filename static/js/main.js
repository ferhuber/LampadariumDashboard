// main.js
document.addEventListener('DOMContentLoaded', function() {
    console.log(chartData);  // Check the data
    var ctx = document.getElementById('myChart').getContext('2d');
    
    // Use the global chartData variable
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.months,
            datasets: [{
                label: 'Expenses',
                data: chartData.expenses,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }, {
                label: 'Income',
                data: chartData.income,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
