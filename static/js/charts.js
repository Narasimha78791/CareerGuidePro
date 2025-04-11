document.addEventListener('DOMContentLoaded', function() {
    // Market Trends Chart
    const trendChartElement = document.getElementById('market-trends-chart');
    if (trendChartElement) {
        const ctx = trendChartElement.getContext('2d');
        
        // Parse data from the data attribute
        const rawData = trendChartElement.dataset.trends;
        const trendsData = JSON.parse(rawData);
        
        // Prepare data for the chart
        const labels = trendsData.map(item => item.name);
        const demandData = trendsData.map(item => (item.demand_level * 100).toFixed(0));
        const salaryData = trendsData.map(item => (item.salary_range_min + item.salary_range_max) / 2);
        
        const trendChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Demand Level (%)',
                        data: demandData,
                        backgroundColor: 'rgba(54, 162, 235, 0.8)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Demand Level (%)'
                        }
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                return `Avg. Salary: $${salaryData[index].toLocaleString()}`;
                            }
                        }
                    },
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Career Demand Levels',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
    
    // Career Salary Range Chart
    const salaryChartElement = document.getElementById('salary-range-chart');
    if (salaryChartElement) {
        const ctx = salaryChartElement.getContext('2d');
        
        // Parse data from the data attribute
        const careerName = salaryChartElement.dataset.career;
        const minSalary = parseInt(salaryChartElement.dataset.min);
        const maxSalary = parseInt(salaryChartElement.dataset.max);
        
        const salaryChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [careerName],
                datasets: [
                    {
                        label: 'Salary Range',
                        data: [maxSalary - minSalary],
                        backgroundColor: 'rgba(75, 192, 192, 0.8)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        barPercentage: 0.5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {
                    x: {
                        min: minSalary,
                        max: maxSalary,
                        title: {
                            display: true,
                            text: 'Salary (USD)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Salary Range: $${minSalary.toLocaleString()} - $${maxSalary.toLocaleString()}`;
                            }
                        }
                    },
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Salary Range',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
    
    // Recommendations Score Chart
    const recommendationChartElement = document.getElementById('recommendation-scores-chart');
    if (recommendationChartElement) {
        const ctx = recommendationChartElement.getContext('2d');
        
        // Parse data from the data attribute
        const rawData = recommendationChartElement.dataset.recommendations;
        const recommendationsData = JSON.parse(rawData);
        
        // Prepare data for the chart
        const labels = recommendationsData.map(item => item.name);
        const scores = recommendationsData.map(item => (item.score * 100).toFixed(1));
        
        const recommendationChart = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Match Score (%)',
                        data: scores,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)',
                            'rgba(83, 102, 255, 0.7)',
                            'rgba(40, 159, 64, 0.7)',
                            'rgba(210, 99, 132, 0.7)'
                        ],
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Match Score: ${context.raw}%`;
                            }
                        }
                    },
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Career Match Scores',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
});
