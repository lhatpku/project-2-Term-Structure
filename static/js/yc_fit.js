var url = `/betas`;

d3.json(url).then(function(beta_data){

    var formatDateIntoYear = d3.timeFormat("%Y");
    var formatDate = d3.timeFormat("%b %Y");
    var parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

    var startDate = new Date(beta_data[0].Date);
    var endDate = new Date(beta_data[beta_data.length-1].Date);

    var margin = {top:20, right:40, bottom:80, left:50};
    var width = 560 - margin.left - margin.right;
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
        .attr("fill","#4682b4")
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
        .attr("fill","#8b4513")
        .text(formatDate(startDate))
        .attr("transform", "translate(0," + (25) + ")");

    //////// Generate Yield Curve ////////////
    var lam_t = .0609;

    var maturities_output = [...[1,2],...d3.range(3,360,3)];

    var yield_rate_output_list = [];

    beta_data.forEach((d) => {

        var yield_rates = maturities_output.map((y) => {

            var load2 = (1. - Math.exp(-lam_t*y)) / (lam_t*y);
            var load3 = ((1.- Math.exp(-lam_t*y)) / (lam_t*y)) - Math.exp(-lam_t*y);

            var yield_rate = d.beta1 + d.beta2 * load2 + d.beta3 * load3;

            return {"rate":yield_rate,"maturity":y};

        });

        var betas = {"beta1":d.beta1,"beta2":d.beta2,"beta3":d.beta3}

        yield_rate_output_list.push({"Date":d.Date,"Data":yield_rates,"Beta":betas});

    })

    var yield_rate_raw_list = [];
    beta_data.forEach((d) => {

        yield_rate_raw = [];
        yield_rate_raw.push({"maturity":1,"rate":d["MO_1"]});
        yield_rate_raw.push({"maturity":2,"rate":d["MO_2"]});
        yield_rate_raw.push({"maturity":3,"rate":d["MO_3"]});
        yield_rate_raw.push({"maturity":6,"rate":d["MO_6"]});
        yield_rate_raw.push({"maturity":12,"rate":d["YR_1"]});
        yield_rate_raw.push({"maturity":24,"rate":d["YR_2"]});
        yield_rate_raw.push({"maturity":36,"rate":d["YR_3"]});
        yield_rate_raw.push({"maturity":60,"rate":d["YR_5"]});
        yield_rate_raw.push({"maturity":84,"rate":d["YR_7"]});
        yield_rate_raw.push({"maturity":120,"rate":d["YR_10"]});
        yield_rate_raw.push({"maturity":240,"rate":d["YR_20"]});
        yield_rate_raw.push({"maturity":360,"rate":d["YR_30"]});

        yield_rate_raw = yield_rate_raw.filter((d) => d.rate !== null);

        yield_rate_raw_list.push({"Date":d.Date,"Data":yield_rate_raw});

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

    // create dotted line group and append to graph
    const dottedLines = graph.append('g')
        .attr('class', 'lines')
        .style('opacity', 0);

    // create x dotted line and append to dotted line group
    const xDottedLine = dottedLines.append('line')
        .attr('stroke', '#aaa')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', 4);

    // create y dotted line and append to dotted line group
    const yDottedLine = dottedLines.append('line')
        .attr('stroke', '#aaa')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', 4);


    var dataset = yield_rate_output_list.map((d) => {
        d.Data = d.Data;
        d.Beta = d.Beta
        d.Date = parseDate(d.Date);
        return d;
    });

    var dataset_raw = yield_rate_raw_list.map((d) => {
        d.Data = d.Data;
        d.Date = parseDate(d.Date);
        return d;
    });

    drawPlot(dataset[0].Data,dataset_raw[0].Data,dataset[0].Date);
    updateTable(dataset[0].Beta);
    
    playButton
    .on("click", function() {
        var button = d3.select(this);
        console.log(button.html());
        if (button.html().includes(`<i class="material-icons">stop</i>`)) {
            moving = false;
            clearInterval(timer);
            // timer = 0;
            button.html(`<i class="material-icons">play_arrow</i>`);
        } else {
            moving = true;
            timer = setInterval(step, 100);
            button.html(`<i class="material-icons">stop</i>`);
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
            playButton.html(`<i class="material-icons">play_arrow</i>`);
            console.log("Slider moving: " + moving);
        }
    }

    function drawPlot(data,data_raw,date) {

        // x and y scale
        var x_ = d3.scaleLinear().range([0,width]);
        var y_ = d3.scaleLinear().range([height,0]);

        // D3 line generator
        var line = d3.line()
        .x(d => x_(d.maturity))
        .y(d => y_(d.rate));

        // Line path element
        x_.domain(d3.extent(data,d => d.maturity));
        y_.domain([-0.5,9]);

        // Update data path
        path.data([data])
            .attr('fill','none')
            .attr('stroke','#87cefa')
            .attr('stroke-width',2)
            .attr('d',line);

        // create circles for points
        const circles = graph.selectAll('circle')
            .data(data_raw);

        // remove unwanted points
        circles.exit().remove();

        // update current points
        circles.attr('r', '4')
        .attr('cx', d => x_(d.maturity))
        .attr('cy', d => y_(d.rate));

        // add new points
        circles.enter()
            .append('circle')
            .attr('r', '4')
            .attr('cx', d => x_(d.maturity))
            .attr('cy', d => y_(d.rate))
            .attr('fill', '#ffa07a');

        // add event listeners to circle (and show dotted lines)
        graph.selectAll('circle')
        .on('mouseover', (d, i, n) => {
            d3.select(n[i])
                .transition().duration(100)
                .attr('r', 8)
                .attr('fill', '#a0522d');
            // set x dotted line coords (x1,x2,y1,y2)
            xDottedLine
                .attr('x1', x_(d.maturity))
                .attr('x2', x_(d.maturity))
                .attr('y1', height)
                .attr('y2', y_(d.rate));
            // set y dotted line coords (x1,x2,y1,y2)
            yDottedLine
                .attr('x1', 0)
                .attr('x2', x_(d.maturity))
                .attr('y1', y_(d.rate))
                .attr('y2', y_(d.rate));
            // show the dotted line group (opacity)
            dottedLines.style('opacity', 1);
        })
        .on('mouseleave', (d,i,n) => {
            d3.select(n[i])
                .transition().duration(100)
                .attr('r', 4)
                .attr('fill', '#ffa07a');
                // hide the dotted line group (opacity)
                dottedLines.style('opacity', 0)
        });


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

    function updateTable(betas) {

        d3.select("#fit-stat").html("");

        var selection = d3.select("#fit-stat");

        var betas_keys = Object.keys(betas);

        betas_keys.forEach((d) => {

            var tr_new = selection.append("tr");
            tr_new.append("td").text(d);
            tr_new.append("td").text(Math.round(betas[d]*1000)/1000);
        
        });

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
        var newData_raw = dataset_raw.filter(function(d) {
            return d.Date <= h;
        })

        if (newData.length < 1) {
            newData = dataset[0];
        }
        if (newData_raw.length < 1) {
            newData_raw = dataset_raw[0];
        }

        drawPlot(newData[newData.length-1].Data,newData_raw[newData_raw.length-1].Data,newData[newData.length-1].Date);
        updateTable(newData[newData.length-1].Beta)
    }

})