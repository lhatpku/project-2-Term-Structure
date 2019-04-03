var url = `/bonds_fit`;
var radios = document.forms["ETFs"].elements["ETF"];

var description_dict = {"SHV":"SHV tracks a market-weighted index of debt issued by the U.S. Treasury. Remaining maturity must be 1-12 months.",
"VGSH":"VGSH tracks a market weighted index of fixed income securities issued by the U.S. Treasury, excluding inflation-protected securities, with maturities of 1-3 years.",
"TLH":"TLH tracks a market-weighted index of debt issued by the U.S. Treasury. Remaining maturity must be between 10 and 20 years."};

function drawchart(data,ticker) {

    var bond_line_data = data[ticker]

    var bond_line_series1 = bond_line_data['y_fit'].map(d => [new Date(d.Date).valueOf() ,Math.round(d.return*100000)/100000]);
    var bond_line_series2 = bond_line_data['y'].map(d => [new Date(d.Date).valueOf() ,Math.round(d.return*100000)/100000]);

    var pie_plot_pair = bond_line_data['params'].filter(d => d.param >= 0.01).map(d => ['YTM - '+d.maturity/12,d.param]);

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
            labels: {
                formatter: function() {
                  return new Date(this.value).toLocaleDateString();
                }
            },
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

    var maturity_data = bonds_fit_data['SHV']['params'];
    var weighted_maturity = 0;
    maturity_data.forEach((d) => {
        weighted_maturity = weighted_maturity + (d.maturity * d.param) / 12;
    });

    drawchart(bonds_fit_data,'SHV');
    d3.select("#ETF-summary").text(description_dict['SHV']);
    d3.select("#weighted-maturity").text(Math.round(weighted_maturity*10000)/10000);

    for(var i = 0, max = radios.length; i < max; i++) {

        radios[i].onclick = function() {

            selected_ticker = this.value;

            maturity_data = bonds_fit_data[selected_ticker]['params'];
            var weighted_maturity = 0;
            maturity_data.forEach((d) => {
                weighted_maturity = weighted_maturity + (d.maturity * d.param) / 12;
            });
            d3.select("#weighted-maturity").text(Math.round(weighted_maturity*10000)/10000);

            drawchart(bonds_fit_data,selected_ticker);
            d3.select("#ETF-summary").text(description_dict[selected_ticker]);
        }
    }

});
