var config = {
    type: 'pie',
    data: {
      datasets: [{
        data: {{ data|safe }},
        backgroundColor: ['rgb(255, 205, 86)', 'rgb(54, 162, 235)', 'rgb(0, 255, 0)', 'rgb(255, 99, 132)'],
      }],
        labels: {{ labels|safe }},
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'left',
        },
        title: {
          display: true,
          text: 'Exécution du budget'
        }
      }
    },
};

window.onload = function() {
  var ctx = document.getElementById('pie-chart').getContext('2d');
  window.myPie = new Chart(ctx, config);
};


