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
          name: key + ' - month yield rate',
          x: unpack(yield_data, 'Date'),
          y: unpack(yield_data, key),
          line: {color: colour(key)}
        }

        data.push(trace)
      
      }

    });

  
    // var trace1 = {
    //   type: "scatter",
    //   mode: "lines",
    //   name: '1-year',
    //   x: unpack(yield_data, 'Date'),
    //   y: unpack(yield_data, '12'),
    //   line: {color: '#17BECF'}
    // }
    
    // var trace2 = {
    //   type: "scatter",
    //   mode: "lines",
    //   name: '5-year',
    //   x: unpack(yield_data, 'Date'),
    //   y: unpack(yield_data, '60'),
    //   line: {color: '#7F7F7F'}
    // }
    
    // var data = [trace1,trace2];
    
    var layout = {
      title: 'Basic Time Series',
    };
    
    Plotly.newPlot('chart', data, layout);
    
  })
}

buildCharts();