var url = `/monthly_yields`;

d3.json(url).then(function(yield_data){

    var data = []

    yield_data.forEach((d,j) => {
        var y= j;

        var keys = Object.keys(d);
        var values = Object.values(d);

        for (i=1; i < keys.length; i++ ){
            var x = i;
            var z = values[i];

            if (z < 20){
                data.push([x,y,z])
            } else {continue}
        } 
    })


    console.log(data)

    anychart.onDocumentReady(function() {
        // create chart
        var chart = anychart.surface()
        // set data
        chart.data(data);
    
        // hide the last label in Y axis
        chart.yAxis().drawLastLabel(false);
    
        // display chart
        chart.container('3d-chart').draw();
    });
    
    
})