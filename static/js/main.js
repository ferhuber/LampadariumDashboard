document.addEventListener('DOMContentLoaded', function () {
    var ctx = document.getElementById('myChart').getContext('2d');

    if (!ctx || selectedMonth !== null) {
        document.getElementById('myChart').style.display = 'none';
        document.getElementById('totals').style.display = 'none';
        document.getElementById('expenses').style.display = 'none';
        document.getElementById('income').style.display = 'none';
        document.getElementById('chartContainer').style.display = 'none';

        // Initialize the pie chart for aggregated expenses
        var pieCtx = document.getElementById('expensesPieChart').getContext('2d');
        var expensesPieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: aggregatedExpensesLabels, // Array of category names
                datasets: [{
                    data: aggregatedExpensesData, // Array of corresponding amounts
                    backgroundColor: [
                        // Define colors for each slice
                        'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta', 'lime', 'pink', 'teal', 'lavender'
                        // Add more colors if you have more categories
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                title: {
                    display: true,
                    text: 'Expenses Breakdown for ' + selectedMonth
                },
                plugins: {
                    legend: {
                        position: 'right',
                        // You can also customize other legend properties here

                    }
                },
            }
        });
        // Initialize the pie chart for aggregated deposits
        var pieCtx = document.getElementById('depositsPieChart').getContext('2d');
        var depositsPieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: aggregatedDepositsLabels, // Array of category names
                datasets: [{
                    data: aggregatedDepositsData, // Array of corresponding amounts
                    backgroundColor: [
                        // Define colors for each slice
                        'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta', 'lime', 'pink', 'teal', 'lavender'
                        // Add more colors if you have more categories
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                title: {
                    display: true,
                    text: 'Deposit Breakdown for ' + selectedMonth
                },
                plugins: {
                    legend: {
                        position: 'right',
                        // You can also customize other legend properties here

                    }
                },
            }
        });

    } else {
        // Display the chart and totals if no specific month is selected
        document.getElementById('myChart').style.display = 'block';
        document.getElementById('chartContainer').style.display = 'block';
        document.getElementById('totals').style.display = 'block';

    }
    // Display total expenses, income, and profit
    document.getElementById('total-expenses').textContent = '$' + totalExpenses.toFixed(2);
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
    function setFormAction(action) {
        document.getElementById('formAction').value = action;
        document.getElementById('dashboardForm').action = action;
    }
});
