url='/sp500'
d3.json(url).then(a => {

   var tSpread=a.map(d =>d.YR_10-d.YR_2)

   var tenYear = a.map(d =>d.return10y)

   var date = a.map(function(d){
       var tab_date=d.Date.split('-')
       var date_utc = Date.UTC(parseInt(tab_date[0]),parseInt(tab_date[1])-1, parseInt(tab_date[2]));
       return date_utc
   });


   var yieldData = []

   for (i=0; i< date.length; i++){
       if (tSpread[i] != null && tSpread[i] != 0){
       yieldData.push([date[i], tSpread[i]])
       }
   }

   console.log(yieldData)

   var sp500Data = []

   for (i=0; i< date.length; i++){
       if (tenYear[i] != null) {
       sp500Data.push([date[i], tenYear[i]])
       }
   }

   console.log(sp500Data)

   url2='/gdp'

   d3.json(url2).then(b => {

       var gdpRate = b.map(d => d.A191RP1Q027SBEA)
       var gdpDate = b.map(function(d) {
           var tab_date=d.DATE.split('\/')
           var date_utc = Date.UTC(parseInt(tab_date[2]),parseInt(tab_date[0])-1, parseInt(tab_date[1]));
           return date_utc
       });


       var gdpData = []

       for (i=0; i< gdpDate.length; i++){
           gdpData.push([gdpDate[i], gdpRate[i]])
       }

Highcharts.chart('economy-chart', {
   chart: {
     zoomType: 'xy'
   },
   title: {
     text: 'Economic Comparisons'
   },
   subtitle: {
     text: 'Comparing SP500 Returns and GDP Growth Rate with Yield Rate Spreads'
   },
   xAxis: {
     type: 'datetime',
     dateTimeLabelFormats: {
       year: '%Y'
     },
     title: {
       text: 'Date'
     },
     crosshair: true
   },
   yAxis: [{
       labels: {
           format: '{value} %'
       ,
       style: {
           color: Highcharts.getOptions().colors[2]
       }},
       title: {
       text: 'Rate(%)',
       color: Highcharts.getOptions().colors[0]
     },
     opposite: true
   //   min: 0
   }, {
       gridLineWidth: 0,
       title: {
           text: ''
       ,
       style: {
           color: Highcharts.getOptions().colors[0]
       }},
       labels: {
           format: '{value} %'
       ,
       style: {
           color: Highcharts.getOptions().colors[0]
       }}
   }, {
       gridLineWidth: 0,
       title: {
           text: ""
       ,
       style: {
           color: Highcharts.getOptions().colors[1]
       }},
       labels: {
           formate: '{value} %',
           style: {
               color: Highcharts.getOptions().colors[1]
           }
       },
       opposite: true
   }],

   tooltip: {
       shared: true,
       headerFormat: '<b>{series.name}</b><br>',
       pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
   },

   legend: {
     layout: 'vertical',
     align: 'left',
     x: 30,
     verticalAlign: 'top',
     y: 10,
     floating: true,
     backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || 'rgba(255,255,255,0.25)'
   },

   plotOptions: {
     spline: {
       marker: {
         enabled: true
       }
     },
     column: {
         pointWidth: 5,
         color:  'rgba(150, 165, 188, 0.50)'

     }
   },
   // of 1970/71 in order to be compared on the same x axis. Note
   // that in JavaScript, months start at 0 for January, 1 for February etc.
   series: [{
     name: "SP500 Returns",
     data: sp500Data,
     dashStyle:'Solid',
     tooltip: {
         valueSuffix: '%'
     }
   }, {
     name: "Yield Rate Spread (10Y - 2Y)",
     data: yieldData,
     dashStyle:'Solid',
     tooltip: {
         valueSuffix: '%'
     }
   }, {
     name: "GDP Annualized Quarterly Growth Rate",
     type: 'column',
     data: gdpData,
     tooltip: {
         valueSuffix: '%'
     }
   }]
 });


   })
})