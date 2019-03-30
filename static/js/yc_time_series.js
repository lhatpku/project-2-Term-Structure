var yc_dropdown_list = [1,2,3,6,12,24,36,60,84,120,240,360];

var form = document.querySelector('form');
var yc_date_start = document.querySelector('#yc-date-start');
var yc_date_end = document.querySelector('#yc-date-end');
var yc_select = document.querySelector('#yc-select');

function remove(array, element) {
  return array.filter(el => el !== element);
}

function unpack(rows, key) {
  return rows.map(function(row) { return row[key]; });
}


function buildCharts() {

  // @TODO: Build a bubble Chart
  const colour = d3.scaleOrdinal(d3['schemeSet3']);
  var url = `/yields`;

  d3.json(url).then(function(yield_data){
  
    var output_list = remove(Object.keys(yield_data[0]),'Date');

    colour.domain(output_list);

    var data = [];

    output_list.forEach((key) => {

      if (key !== "Date") {

        trace = {
          type: "scatter",
          mode: "lines",
          name: key + ' - YTM',
          x: unpack(yield_data, 'Date'),
          y: unpack(yield_data, key),
          line: {color: colour(key)}
        }

        data.push(trace)
      
      }

    });
    
    var layout = {
      title: 'Yield Curve Time Series',
      showlegend: true,
      legend: {"orientation": "h",},
      yaxis: {
        title: 'Yield Rate (%)'
      },
      xaxis:{
        type: 'date',
        "tickformat": "%Y-%m-%d"
      }
    };
    
    Plotly.newPlot('timeseries-chart', data, layout,{showSendToCloud: true});

    // User Selection
    form.addEventListener('submit',(e) => {

      e.preventDefault();
    
      var plot_date_start = yc_date_start.value;
      var plot_date_end = yc_date_end.value;
      var plot_yc_select = $('#yc-select').val();

      if (plot_date_start === "") {
        plot_date_start = yield_data[0]["Date"];
      }

      if (plot_date_end === "") {
        plot_date_end = yield_data[yield_data.length - 1]["Date"];
      }

      var startDate = new Date(plot_date_start);
      var endDate = new Date(plot_date_end);

      var yield_data_filter = yield_data.filter(function (d) {
        var Date_obj = new Date(d.Date);
        return (Date_obj >= startDate && Date_obj <= endDate);
      });

      if (plot_yc_select.includes('all')) {

        data = [];

        output_list.forEach((key) => {

          if (key !== "Date") {

            trace = {
              type: "scatter",
              mode: "lines",
              name: key + ' - YTM',
              x: unpack(yield_data_filter, 'Date'),
              y: unpack(yield_data_filter, key),
              line: {color: colour(key)}
            }

            data.push(trace)
      
          }

        });

      }

      else {

        data = [];

        plot_yc_select.forEach((key) => {

          if (key !== "Date") {

            trace = {
              type: "scatter",
              mode: "lines",
              name: key + ' - YTM',
              x: unpack(yield_data_filter, 'Date'),
              y: unpack(yield_data_filter, key),
              line: {color: colour(key)}
            }

            data.push(trace)
      
          }

        });

      }
      
      Plotly.newPlot('timeseries-chart', data, layout,{showSendToCloud: true});

    });
       
  })
}

buildCharts();

