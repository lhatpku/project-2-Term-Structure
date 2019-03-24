var url = `/betas`;

d3.json(url).then(function(beta_data){

    var formatDateIntoYear = d3.timeFormat("%Y");
    var formatDate = d3.timeFormat("%b %Y");
    var parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

    var startDate = new Date(beta_data[0].Date);
    var endDate = new Date(beta_data[beta_data.length-1].Date);

    var margin = {top:40, right:40, bottom:80, left:30};
    var width = 480 - margin.left - margin.right;
    var height = 480 - margin.top - margin.bottom;

    var svg = d3.select("#vis")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);  

    ////////// slider //////////

    var moving = false;
    var currentValue = 0;
    var targetValue = width;

    var playButton = d3.select("#play-button");
        
    var x = d3.scaleTime()
        .domain([startDate, endDate])
        .range([0, targetValue])
        .clamp(true);

    var slider = svg.append("g")
        .attr("class", "slider")
        .attr("transform", "translate(" + margin.left + "," + (height + margin.top + 40) + ")");

    slider.append("line")
        .attr("class", "track")
        .attr("x1", x.range()[0])
        .attr("x2", x.range()[1])
    .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "track-inset")
    .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "track-overlay")
        .call(d3.drag()
            .on("start.interrupt", function() { slider.interrupt(); })
            .on("start drag", function() {
            currentValue = d3.event.x;
            update(x.invert(currentValue)); 
            })
        );

    slider.insert("g", ".track-overlay")
        .attr("class", "ticks")
        .attr("transform", "translate(0," + 18 + ")")
    .selectAll("text")
        .data(x.ticks(5))
        .enter()
        .append("text")
        .attr("x", x)
        .attr("y", -15)
        .attr("text-anchor", "middle")
        .text(function(d) { return formatDateIntoYear(d); });

    var handle = slider.insert("circle", ".track-overlay")
        .attr("class", "handle")
        .attr("r", 9);

    var label = slider.append("text")  
        .attr("class", "label")
        .attr("text-anchor", "middle")
        .text(formatDate(startDate))
        .attr("transform", "translate(0," + (25) + ")");

    //////// Generate Yield Curve ////////////
    var lam_t = .0609;

    var maturities_output = d3.range(3,360,3);

    var yield_rate_output_list = [];

    beta_data.forEach((d) => {

        var yield_rates = maturities_output.map((y) => {

            var load2 = (1. - Math.exp(-lam_t*y)) / (lam_t*y);
            var load3 = ((1.- Math.exp(-lam_t*y)) / (lam_t*y)) - Math.exp(-lam_t*y);

            var yield_rate = d.beta1 + d.beta2 * load2 + d.beta3 * load3;

            return {"rate":yield_rate,"maturity":y};

        });

        yield_rate_output_list.push({"Date":d.Date,"Data":yield_rates});

    })

    ////////// plot //////////
    const graph = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const xAxisGroup = graph.append('g')
        .attr('class','x-axis')
        .attr('transform',`translate(0,${height})`);

    const yAxisGroup = graph.append('g')
        .attr('class','y-axis');

    const path = graph.append('path');


    var dataset = yield_rate_output_list.map((d) => {
        d.Data = d.Data;
        d.Date = parseDate(d.Date);
        return d;
    });

    console.log(dataset);

    drawPlot(dataset[0].Data);
    
    playButton
    .on("click", function() {
    var button = d3.select(this);
    if (button.text() == "Pause") {
        moving = false;
        clearInterval(timer);
        // timer = 0;
        button.text("Play");
    } else {
        moving = true;
        timer = setInterval(step, 100);
        button.text("Pause");
    }
    console.log("Slider moving: " + moving);
    })

    
    function step() {
    update(x.invert(currentValue));
    currentValue = currentValue + (targetValue/151);
    if (currentValue > targetValue) {
        moving = false;
        currentValue = 0;
        clearInterval(timer);
        // timer = 0;
        playButton.text("Play");
        console.log("Slider moving: " + moving);
    }
    }

    function drawPlot(data) {

        // x and y scale
        var x_ = d3.scaleLinear().range([0,width]);
        var y_ = d3.scaleLinear().range([height,0]);

        // D3 line generator
        var line = d3.line()
        .x(d => x_(d.maturity))
        .y(d => y_(d.rate));

        // Line path element
        x_.domain(d3.extent(data,d => d.maturity));
        y_.domain([0,d3.max(data,d => d.rate)]);

        // Update data path
        path.data([data])
            .attr('fill','none')
            .attr('stroke','#708090')
            .attr('stroke-width',2)
            .attr('d',line);
        
        const xAxis = d3.axisBottom(x_)
            .ticks(10)
            .tickFormat(d => d + '-month');

        const yAxis = d3.axisLeft(y_)
            .ticks(5)
            .tickFormat(d => d + ' %');

        // Call Axis
        xAxisGroup.call(xAxis);
        yAxisGroup.call(yAxis);

        // Rotate axis text
        xAxisGroup.selectAll('text')
            .attr('text-anchor','end');
            
    }

    function update(h) {
    // update position and text of label according to slider scale
    handle.attr("cx", x(h));
    label
        .attr("x", x(h))
        .text(formatDate(h));

    // filter data set and redraw plot
    var newData = dataset.filter(function(d) {
        return d.Date <= h;
    })
    if (newData.length < 1) {
        newData = dataset[0];
    }
    drawPlot(newData[newData.length-1].Data);
    }

})