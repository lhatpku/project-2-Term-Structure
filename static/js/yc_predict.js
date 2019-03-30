var url = `/betas_all`;
var parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

var last_hist_date = Date.parse("March 26, 2019");

d3.json(url).then(function(beta_data_all){

    var beta1_series = beta_data_all.map(d => [d.Date,d.beta1]);
    var beta2_series = beta_data_all.map(d => [d.Date,d.beta2]);
    var beta3_series = beta_data_all.map(d => [d.Date,d.beta3]);

    Highcharts.chart('predict-chart', {
        title: {
        text: 'Beta(s) Prediction'
        },
        subtitle: {
        text: 'The time series of predicted beta(s)'
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
        colors: ['#6CF', '#39F', '#add8e6'],
        series: [
            {
                name: "Beta 1",
                data: beta1_series,
                zoneAxis: 'x',
                zones: [{
                    value: last_hist_date
                }, {
                    dashStyle: 'dot'
                }]
            },
            {
                name: "Beta 2",
                data: beta2_series,
                zoneAxis: 'x',
                zones: [{
                    value: last_hist_date
                }, {
                    dashStyle: 'dot'
                }]
            },
            {
                name: "Beta 3",
                data: beta3_series,
                zoneAxis: 'x',
                zones: [{
                    value: last_hist_date
                }, {
                    dashStyle: 'dot'
                }]
            }
        ]
    });

});