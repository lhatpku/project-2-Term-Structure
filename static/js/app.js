var yc_dropdown_list = [1,2,3,6,12,24,36,60,84,120,240,360];

function remove(array, element) {
  return array.filter(el => el !== element);
}

function buildCharts() {

  // @TODO: Build a bubble Chart
  const colour = d3.scaleOrdinal(d3['schemeSet3']);
  var url = `/yields`;

  d3.json(url).then(function(yield_data){
  
    function unpack(rows, key) {
      return rows.map(function(row) { return row[key]; });
    }

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
	    legend: {"orientation": "h",}
    };
    
    Plotly.newPlot('chart', data, layout,{showSendToCloud: true});
    
  })
}



buildCharts();