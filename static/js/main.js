document.addEventListener('DOMContentLoaded', function() {
    var ctx = document.getElementById('myChart').getContext('2d');

    if (!ctx || selectedMonth !== null) {
        document.getElementById('myChart').style.display = 'none';
        document.getElementById('totals').style.display = 'none';

    }else {
            // Display the chart and totals if no specific month is selected
            document.getElementById('myChart').style.display = 'block';
            document.getElementById('totals').style.display = 'block';
    
}
// Display total expenses, income, and profit
document.getElementById('total-expenses').textContent = '$' +  totalExpenses.toFixed(2);
document.getElementById('total-income').textContent = '$' + totalIncome.toFixed(2);
// Calculate and display profit as a percentage of total income
var profitPercentage = totalIncome > 0 ? ((profit / totalIncome) * 100) : 0;
document.getElementById('profit').textContent = profitPercentage.toFixed(2) + '%';


    // Initialize the chart when a specific month is not selected
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
