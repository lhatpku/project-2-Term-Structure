var url = `/bonds_fit`;
var radios = document.forms["ETFs"].elements["ETF"];

function drawchart(data,ticker) {

    var bond_line_data = data[ticker]

    var bond_line_series1 = bond_line_data['y_fit'].map(d => [d.Date,Math.round(d.return*100000)/100000]);
    var bond_line_series2 = bond_line_data['y'].map(d => [d.Date,Math.round(d.return*100000)/100000]);

    var pie_plot_pair = bond_line_data['params'].filter(d => d.param >= 0.01).map(d => ['YTM - '+d.maturity,d.param]);

    var others_weight = d3.sum(bond_line_data['params'].filter(d => d.param < 0.01).map(d => d.param));
    pie_plot_pair.push(['Others',others_weight])

    Highcharts.chart('bonds-fit-line', {
        title: {
        text: 'Bond Fitting'
        },
        subtitle: {
        text: 'Zero Coupon Bond Derived from Yield Curve versus ETF Historical Returns'
        },
        chart: {
            type: 'spline'
        },
        xAxis: {
            type: 'datetime',
            title: {
              text: 'Date'
            }
        },
        yAxis: {
            title: {
              text: 'Return'
            }
        },
        colors: ['#6CF', '#39F'],
        series: [
            {
                name: "Fitting Returns",
                data: bond_line_series1
            },
            {
                name: "ETF Returns",
                data: bond_line_series2
            },
           
        ]
    });

    Highcharts.chart('bonds-fit-pie', {
        chart: {
        type: 'pie',
        options3d: {
            enabled: true,
            alpha: 45,
            beta: 0
        }
        },
        title: {
            text: 'Bond ETF Fitting Demo'
        },
        subtitle: {
            text: 'The fitting weight of the Bond ETF to each zero coupon bond'
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            depth: 35,
            dataLabels: {
            enabled: true,
            format: '{point.name}'
            }
        }
        },
        series: [{
            type: 'pie',
            name: 'Bond Fitting Weight',
            data: pie_plot_pair
        }]
    });

};

d3.json(url).then(function(bonds_fit_data){

    drawchart(bonds_fit_data,'SHV')

    for(var i = 0, max = radios.length; i < max; i++) {
        
        radios[i].onclick = function() {
            selected_ticker = this.value;
            drawchart(bonds_fit_data,selected_ticker);
        }
    }

});

