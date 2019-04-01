var url = `/monthly_yields`;

anychart.onDocumentReady(function() {


    d3.json(url).then(function(yield_data) {

        data=[]

        yield_data.forEach((d,j) => {
                    var x= parseInt(d.maturity);
                    var y= d.Date.qyear;
                    var z= d.yield_rates
                    data.push([x,y,z])
                })

        console.log(data)
        // create chart
        var chart = anychart.surface(data)

        console.log("surface")
    
        chart.title('3D Surface Plot of Yield Rates Over Time');

        chart.padding(0,0,0,0);

        chart.rotationY(15);
        chart.rotationZ(45);

        // enable X/Y minor ticks and labels
        chart.xAxis().minorTicks().enabled(true);
        chart.xAxis().minorLabels().enabled(true);
        chart.yAxis().minorTicks().enabled(true);
        chart.yAxis().minorLabels().enabled(true);

        // set X axis scale maximum
        chart.xScale().maximum(360);
        chart.xScale().minimum(0)

        // set Y scale minimum/maximum
        chart.yScale().minimum(1990);
        chart.yScale().maximum(2019);

        chart.zScale().minimum(-1);
        chart.zScale().maximum(11)


        

        // hide the last label in Y axis
        chart.yAxis().drawLastLabel(false);

        // set scales ticks intervals
        chart.xScale().ticks().interval(100);
        chart.yScale().ticks().interval(12);
        chart.zScale().ticks().interval(0);

        // set X/Y/Z axis labels font size
        chart.xAxis().labels().fontSize(10);
        chart.xAxis().minorLabels().fontSize(10);
        chart.yAxis().labels().fontSize(10);
        chart.yAxis().minorLabels().fontSize(10);
        chart.zAxis().labels().fontSize(10);

        // set X axis labels rotation
        chart.xAxis().labels().rotation(90);
        chart.xAxis().minorLabels().rotation(90);

        // set X axis labels format
        // chart.xAxis().labels().format(function () {
        //     return data.x[Math.round(this.value)];
        // });
        // chart.xAxis().minorLabels().format(function () {
        //     return data.x[Math.round(this.value)];
        // });

        // set chart stroke(mesh) settings
        chart.stroke('1 #fff .1');

        // chart.box('#aaa .2')

        // // Create color scale
        // var customColorScale = anychart.scales.linearColor();
        // customColorScale.colors(['#B5DDB6', '#f9ac93', '#96C8E9', '#FF5555']);

        // // Set color scale
        // chart.colorScale(customColorScale);

        var colorScale = anychart.scales.linearColor();
        colorScale.colors(['#2bc0e4', '#eAecc6', '#dd2c00']);

// Set color scale.
        chart.colorScale(colorScale);

        // // enable and configure color range 
        var colorRange=chart.colorRange().enabled(true).orientation('right');

        // colorRange.labels()
        //         .fontColor('#333')
        //         .format(function(){
        //             return this.value.toFixed(1)
        //         });
        // chart.xAxis().stroke('#000')
        // chart.yAxis().stroke('#000')
        // chart.zAxis().stroke('#000');
    
        // display chart
        chart.container('chart').draw();

        
    });
    
    // generate a data set from function

    
    
})