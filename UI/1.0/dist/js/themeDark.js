// parse text json data.
var data = JSON.parse(text);

var chart = LightweightCharts.createChart(document.getElementById("chart"), {
	width: 1270,
	height: 300,
	layout: {
		textColor: '#d1d4dc',
		backgroundColor: '#000000',
	},
	rightPriceScale: {
		scaleMargins: {
			top: 0.3,
			bottom: 0.25,
		},
	},
	crosshair: {
		vertLine: {
			visible: true,
			labelVisible: true,
		},
		horzLine: {
			visible: true,
			labelVisible: false,
		},
		mode: LightweightCharts.CrosshairMode.Normal,
	},
	grid: {
		vertLines: {
			color: 'rgba(42, 46, 57, 0)',
		},
		horzLines: {
			color: 'rgba(42, 46, 57, 0)',
		},
	},
});

var areaSeries = chart.addAreaSeries({
  topColor: 'rgba(38, 198, 218, 0.56)',
  bottomColor: 'rgba(38, 198, 218, 0.04)',
  lineColor: 'rgba(38, 198, 218, 1)',
  lineWidth: 2,
  crossHairMarkerVisible: false,
});

areaSeries.applyOptions({
    lastValueVisible: false,
});

var lineSeries = chart.addLineSeries();

 // const priceLine = areaSeries.createPriceLine({
    // price: 26.5,
    // color: 'rgba(38, 198, 218, 1)',
    // lineWidth: 1,
    // lineStyle: LightweightCharts.LineStyle.Dotted,
    // axisLabelVisible: true,
    // title: 'L/3',
// });

// to remove areaSeries.removePriceLine(priceLine);



// areaSeries.setData([
	// { time: '2018-10-19', value: 26.19 },
	// { time: '2018-10-22', value: 25.87 },
	// { time: '2018-10-23', value: 25.83 },
	// { time: '2018-10-24', value: 25.78 },
	// { time: '2018-10-25', value: 25.82 },
	// { time: '2018-10-26', value: 25.81 },
	// { time: '2018-10-29', value: 25.82 },
	// { time: '2018-10-30', value: 25.71 },
	// { time: '2018-10-31', value: 25.82 },
	// { time: '2018-11-01', value: 25.72 },
	// { time: '2018-11-02', value: 25.74 },
	// { time: '2018-11-05', value: 25.81 },
	// { time: '2018-11-06', value: 25.75 },
	// { time: '2018-11-07', value: 25.73 },
	// { time: '2018-11-08', value: 25.75 },
	// { time: '2018-11-09', value: 25.75 },
	// { time: '2018-11-12', value: 25.76 },
	// { time: '2018-11-13', value: 25.80 },
	// { time: '2018-11-14', value: 25.77 },
	// { time: '2018-11-15', value: 25.75 },
	// { time: '2018-11-16', value: 25.75 },
	// { time: '2018-11-19', value: 25.75 },
	// { time: '2018-11-20', value: 25.72 },
	// { time: '2018-11-21', value: 25.78 },
	// { time: '2018-11-23', value: 25.72 },
	// { time: '2018-11-26', value: 25.78 },
	// { time: '2018-11-27', value: 25.85 },
	// { time: '2018-11-28', value: 25.85 },
	// { time: '2018-11-29', value: 25.55 },
	// { time: '2018-11-30', value: 25.41 },
	// { time: '2018-12-03', value: 25.41 },
	// { time: '2018-12-04', value: 25.42 },
	// { time: '2018-12-06', value: 25.33 },
	// { time: '2018-12-07', value: 25.39 },
	// { time: '2018-12-10', value: 25.32 },
	// { time: '2018-12-11', value: 25.48 },
	// { time: '2018-12-12', value: 25.39 },
	// { time: '2018-12-13', value: 25.45 },
	// { time: '2018-12-14', value: 25.52 },
	// { time: '2018-12-17', value: 25.38 },
	// { time: '2018-12-18', value: 25.36 },
	// { time: '2018-12-19', value: 25.65 },
	// { time: '2018-12-20', value: 25.70 },
	// { time: '2018-12-21', value: 25.66 },
	// { time: '2018-12-24', value: 25.66 },
	// { time: '2018-12-26', value: 25.65 },
	// { time: '2018-12-27', value: 25.66 },
	// { time: '2018-12-28', value: 25.68 },
	// { time: '2018-12-31', value: 25.77 },
	// { time: '2019-01-02', value: 25.72 },
	// { time: '2019-01-03', value: 25.69 },
	// { time: '2019-01-04', value: 25.71 },
	// { time: '2019-01-07', value: 25.72 },
	// { time: '2019-01-08', value: 25.72 },
	// { time: '2019-01-09', value: 25.66 },
	// { time: '2019-01-10', value: 25.85 },
	// { time: '2019-01-11', value: 25.92 },
	// { time: '2019-01-14', value: 25.94 },
	// { time: '2019-01-15', value: 25.95 },
	// { time: '2019-01-16', value: 26.00 },
	// { time: '2019-01-17', value: 25.99 },
	// { time: '2019-01-18', value: 25.60 },
	// { time: '2019-01-22', value: 25.81 },
	// { time: '2019-01-23', value: 25.70 },
	// { time: '2019-01-24', value: 25.74 },
	// { time: '2019-01-25', value: 25.80 },
	// { time: '2019-01-28', value: 25.83 },
	// { time: '2019-01-29', value: 25.70 },
	// { time: '2019-01-30', value: 25.78 },
	// { time: '2019-01-31', value: 25.35 },
	// { time: '2019-02-01', value: 25.60 },
	// { time: '2019-02-04', value: 25.65 },
	// { time: '2019-02-05', value: 25.73 },
	// { time: '2019-02-06', value: 25.71 },
	// { time: '2019-02-07', value: 25.71 },
	// { time: '2019-02-08', value: 25.72 },
	// { time: '2019-02-11', value: 25.76 },
	// { time: '2019-02-12', value: 25.84 },
	// { time: '2019-02-13', value: 25.85 },
	// { time: '2019-02-14', value: 25.87 },
	// { time: '2019-02-15', value: 25.89 },
	// { time: '2019-02-19', value: 25.90 },
	// { time: '2019-02-20', value: 25.92 },
	// { time: '2019-02-21', value: 25.96 },
	// { time: '2019-02-22', value: 26.00 },
	// { time: '2019-02-25', value: 25.93 },
	// { time: '2019-02-26', value: 25.92 },
	// { time: '2019-02-27', value: 25.67 },
	// { time: '2019-02-28', value: 25.79 },
	// { time: '2019-03-01', value: 25.86 },
	// { time: '2019-03-04', value: 25.94 },
	// { time: '2019-03-05', value: 26.02 },
	// { time: '2019-03-06', value: 25.95 },
	// { time: '2019-03-07', value: 25.89 },
	// { time: '2019-03-08', value: 25.94 },
	// { time: '2019-03-11', value: 25.91 },
	// { time: '2019-03-12', value: 25.92 },
	// { time: '2019-03-13', value: 26.00 },
	// { time: '2019-03-14', value: 26.05 },
	// { time: '2019-03-15', value: 26.11 },
	// { time: '2019-03-18', value: 26.10 },
	// { time: '2019-03-19', value: 25.98 },
	// { time: '2019-03-20', value: 26.11 },
	// { time: '2019-03-21', value: 26.12 },
	// { time: '2019-03-22', value: 25.88 },
	// { time: '2019-03-25', value: 25.85 },
	// { time: '2019-03-26', value: 25.72 },
	// { time: '2019-03-27', value: 25.73 },
	// { time: '2019-03-28', value: 25.80 },
	// { time: '2019-03-29', value: 25.77 },
	// { time: '2019-04-01', value: 26.06 },
	// { time: '2019-04-02', value: 25.93 },
	// { time: '2019-04-03', value: 25.95 },
	// { time: '2019-04-04', value: 26.06 },
	// { time: '2019-04-05', value: 26.16 },
	// { time: '2019-04-08', value: 26.12 },
	// { time: '2019-04-09', value: 26.07 },
	// { time: '2019-04-10', value: 26.13 },
	// { time: '2019-04-11', value: 26.04 },
	// { time: '2019-04-12', value: 26.04 },
	// { time: '2019-04-15', value: 26.05 },
	// { time: '2019-04-16', value: 26.01 },
	// { time: '2019-04-17', value: 26.09 },
	// { time: '2019-04-18', value: 26.00 },
	// { time: '2019-04-22', value: 26.00 },
	// { time: '2019-04-23', value: 26.06 },
	// { time: '2019-04-24', value: 26.00 },
	// { time: '2019-04-25', value: 25.81 },
	// { time: '2019-04-26', value: 25.88 },
	// { time: '2019-04-29', value: 25.91 },
	// { time: '2019-04-30', value: 25.90 },
	// { time: '2019-05-01', value: 26.02 },
	// { time: '2019-05-02', value: 25.97 },
	// { time: '2019-05-03', value: 26.02 },
	// { time: '2019-05-06', value: 26.03 },
	// { time: '2019-05-07', value: 26.04 },
	// { time: '2019-05-08', value: 26.05 },
	// { time: '2019-05-09', value: 26.05 },
	// { time: '2019-05-10', value: 26.08 },
	// { time: '2019-05-13', value: 26.05 },
	// { time: '2019-05-14', value: 26.01 },
	// { time: '2019-05-15', value: 26.03 },
	// { time: '2019-05-16', value: 26.14 },
	// { time: '2019-05-17', value: 26.09 },
	// { time: '2019-05-20', value: 26.01 },
	// { time: '2019-05-21', value: 26.12 },
	// { time: '2019-05-22', value: 26.15 },
	// { time: '2019-05-23', value: 26.18 },
	// { time: '2019-05-24', value: 26.16 },
	// { time: '2019-05-28', value: 26.23 },
// ]);

document.getElementById("chart").style.position = 'relative';

var legend = document.createElement('div');
legend.classList.add('legend');
document.getElementById("chart").appendChild(legend);

var firstRow = document.createElement('div');
firstRow.innerText = '';
firstRow.style.color = 'white';
firstRow.style.backgroundColor = "transparent";
legend.appendChild(firstRow);


chart.subscribeCrosshairMove((param) => {
	if (param.time) {
		const price = param.seriesPrices.get(areaSeries);
		const estimatorDelta = showEstimatorDetailNear(areaSeries.coordinateToPrice(param.point.y), price);
		firstRow.innerText = 'Price $' + '  ' + price.toFixed(2) + " , delta $" + (areaSeries.coordinateToPrice(param.point.y) - price ).toFixed(2) + estimatorDelta;
		firstRow.innerText = firstRow.innerText + " . En Leverage x100 la ganancia venta compra es " + doubleTradingSellBuy(price, areaSeries.coordinateToPrice(param.point.y));
	}
  else {
  	firstRow.innerText = '';
  }
});

function doubleTradingSellBuy(sellPrice, actualPrice){
	//var interes_USDT = 0.001 // si es Bitcoin el interes es 0.0003
    var interes_BTC = 0.0003;
	var leverage = 100;
	var tiempo_interes = 1/24;
	var acum_capital = 1;
	var sell_usdt = ((acum_capital * leverage) * sellPrice)* (1 - 0.001)
    var buy_bitcoin = (sell_usdt / actualPrice )* (1-0.001)
    var acum_capital = buy_bitcoin - ((acum_capital * leverage) - acum_capital) * (1+ interes_BTC)**(tiempo_interes)
	return acum_capital;
}

var ACTUALINDEX = 0;
var PREVINDEX = 0;
var NEXTINDEX = 0;

function clearChart(){
	// remove serie
	chart.removeSeries(areaSeries);
	areaSeries = chart.addAreaSeries({
		topColor: 'rgba(38, 198, 218, 0.56)',
		  bottomColor: 'rgba(38, 198, 218, 0.04)',
		  lineColor: 'rgba(38, 198, 218, 1)',
		  lineWidth: 2,
		  crossHairMarkerVisible: false,
	});
	areaSeries.applyOptions({
		lastValueVisible: false,
	});
}

function clearLogs(){
	document.getElementById("logChartContainer").innerHTML = "";
}

function agregarEstimador(price, isLow, etiqueta){
	color = "green"
	if (isLow){
		color = 'rgba(38, 198, 218, 1)'
	}
	const priceLine = areaSeries.createPriceLine({
		price: price,
		color: color,
		lineWidth: 1,
		lineStyle: LightweightCharts.LineStyle.Dotted,
		axisLabelVisible: false,
		title: etiqueta,
	});
	return priceLine;
}

function agregarTick(tick) {
	price = tick.value;
	time = tick.time;
	areaSeries.setData(tick);
}					  
					  
function agregarLogChart(log, date){
	var tr = document.createElement('tr');
	var td1 = document.createElement("td");
	td1.classList.add("td-truncate");
	var div = document.createElement("div");
	div.classList.add("text-truncate");
	div.innerText = log;
	td1.appendChild(div);

	var td2 = document.createElement("td");
	td2.classList.add("text-nowrap");
	td2.classList.add("text-muted");
	td2.innerText = date;
	td2.date = date;
	td2.onclick = function(){ 
		AREA_MARKERS.push(
			{
				time: this.date,
				position: 'aboveBar',
				color: "blue",
				shape: 'circle',
				text: ''
			}
		);
		areaSeries.setMarkers(AREA_MARKERS);
	}
	
	tr.appendChild(td1);
	tr.appendChild(td2);
	
	document.getElementById("logChartContainer").appendChild(tr);
}

function ocultarTodasEstrategiasPrecio(){
	document.getElementById("strategyPriceContainer1").style.visibility = "hidden";
	document.getElementById("strategyPriceContainer2").style.visibility = "hidden";
	document.getElementById("strategyPriceContainer3").style.visibility = "hidden";
	document.getElementById("strategyPriceContainer4").style.visibility = "hidden";
}
function agregarEstrategiaPrecio(name, gananciaTotal, revenuePercent, indexStrategyPrice){
	document.getElementById("strategyPriceName" + indexStrategyPrice).innerText = name;
	document.getElementById("strategyPriceTotal" + indexStrategyPrice).innerText = "$" +  gananciaTotal;
	if(revenuePercent>0){
		sign = "+ ";
		classList = "text-green";
	} else {
		sign = "";
		classList = "text-red";
	}
	document.getElementById("strategyPricePorcentage"+ indexStrategyPrice).classList.add(classList);	
	document.getElementById("strategyPricePorcentage"+ indexStrategyPrice).innerText = sign + revenuePercent.toString() + "%";
	document.getElementById("strategyPriceContainer"+ indexStrategyPrice).style.visibility = "visible";
}

function refreshDashBoard(data){
	
	// Version
	document.getElementById("versionApp").innerText = data.version;
	
	// Strategy Name
	document.getElementById("strategyName").innerText = data.strategyName;
	
	/*
	// Global Revenue
	document.getElementById("strategyRevenue").innerText = "$"  + data.revenue;
	// From to
	document.getElementById("strategyFromTo").innerText = data.from + " - " + data.to;
	// ganancia
	document.getElementById("strategyGanancia").innerText = "ganancia total de " + data.porcentageRevenue + " %";
	// Succes trades
	document.getElementById("strategyTradesSuccess").innerText = data.totalSuccesTransactions;
	document.getElementById("strategyTotalSuccess").innerText = "$" + data.totalSucces + " total";
	document.getElementById("maxWinCont").innerText = "max. d " + data.maxWinCont + " succes seguidos"
	// Lost trades
	document.getElementById("strategyTradesLost").innerText = data.totalLostTransactions;
	document.getElementById("strategyTotalLost").innerText = "$" + data.totalLost + " total";
	document.getElementById("maxLostCont").innerText = "max. d " + data.maxLostCont + " perdidas seguidas";
	*/
	
	// default call first candle
	updateCandleData(0);
	
}

function hiddenAllEstimatorsDetails(){
	var candle_estimators = candle.estimators;
	candle_estimators.low.mediaRef.applyOptions({
    axisLabelVisible: false});
	candle_estimators.low.media2Ref.applyOptions({
    axisLabelVisible: false});
	candle_estimators.low.media3Ref.applyOptions({
    axisLabelVisible: false});
	candle_estimators.low.deltaRef.applyOptions({
    axisLabelVisible: false});
	
	// add high estimators graphic
	candle_estimators.high.mediaRef.applyOptions({
    axisLabelVisible: false});
	candle_estimators.high.media2Ref.applyOptions({
    axisLabelVisible: false});
	candle_estimators.high.media3Ref.applyOptions({
    axisLabelVisible: false});
	candle_estimators.high.deltaRef.applyOptions({
    axisLabelVisible: false});
}

function showEstimatorDetailNear(price, local_price){
	hiddenAllEstimatorsDetails();
	delta = 10;
	var candle_estimators = candle.estimators;
	var message = "";
	// low
	if (price > (candle_estimators.low.media - delta) &&  price < (candle_estimators.low.media + delta)) {
		candle_estimators.low.mediaRef.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador low media es: " + (candle_estimators.low.media - local_price);
	}
	if (price > (candle_estimators.low.mediaIter2 - delta) &&  price < (candle_estimators.low.mediaIter2 + delta)) {
		candle_estimators.low.media2Ref.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador low media 2 es: " + (candle_estimators.low.mediaIter2 - local_price);
	}
	if (price > (candle_estimators.low.mediaIter3 - delta) &&  price < (candle_estimators.low.mediaIter3 + delta)) {
		candle_estimators.low.media3Ref.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador low media 3 es: " + (candle_estimators.low.mediaIter3 - local_price);
	}
	if (price > (candle_estimators.low.delta - delta) &&  price < (candle_estimators.low.delta + delta)) {
		candle_estimators.low.deltaRef.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador low delta es: " + (candle_estimators.low.delta - local_price);
	}
	// high
	if (price > (candle_estimators.high.media - delta) &&  price < (candle_estimators.high.media + delta)) {
		candle_estimators.high.mediaRef.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador high media es: " + (candle_estimators.high.media - local_price);
	}
	if (price > (candle_estimators.high.mediaIter2 - delta) &&  price < (candle_estimators.high.mediaIter2 + delta)) {
		candle_estimators.high.media2Ref.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador high media 2 es: " + (candle_estimators.high.mediaIter2 - local_price);
	}
	if (price > (candle_estimators.high.mediaIter3 - delta) &&  price < (candle_estimators.high.mediaIter3 + delta)) {
		candle_estimators.high.media3Ref.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador high media 3 es: " + (candle_estimators.high.mediaIter3 - local_price);
	}
	if (price > (candle_estimators.high.delta - delta) &&  price < (candle_estimators.high.delta + delta)) {
		candle_estimators.high.deltaRef.applyOptions({
		axisLabelVisible: true});
		message = " la diferencia con estimador high delta  es: " + (candle_estimators.high.delta - local_price);
	}
	return message;
}

function updateEstimadores(candle_estimators, low, high){
	
	// add low estimators graphic
	candle_estimators.low.mediaRef = agregarEstimador(candle_estimators.low.media, true, "low mean");
	candle_estimators.low.media2Ref = agregarEstimador(candle_estimators.low.mediaIter2, true, "low mean 2");
	candle_estimators.low.media3Ref = agregarEstimador(candle_estimators.low.mediaIter3, true, "low mean 3");
	candle_estimators.low.deltaRef = agregarEstimador(candle_estimators.low.delta, true, "low delta");
	
	// add high estimators graphic
	candle_estimators.high.mediaRef = agregarEstimador(candle_estimators.high.media, false, "high mean");
	candle_estimators.high.media2Ref = agregarEstimador(candle_estimators.high.mediaIter2, false, "high mean 2");
	candle_estimators.high.media3Ref = agregarEstimador(candle_estimators.high.mediaIter3, false, "high mean 3");
	candle_estimators.high.deltaRef = agregarEstimador(candle_estimators.high.delta, false, "high delta");	
	
	// update table estimators low
	document.getElementById("low_media_table").innerText = "$" + candle_estimators.low.media.toFixed(2);
	document.getElementById("low_media2_table").innerText = "$" + candle_estimators.low.mediaIter2.toFixed(2);
	document.getElementById("low_media3_table").innerText = "$" + candle_estimators.low.mediaIter3.toFixed(2);
	document.getElementById("low_delta_table").innerText = "$" + candle_estimators.low.delta.toFixed(2);
	document.getElementById("low_table").innerText = "$" + low.toFixed(2);
	
	// update table estimators high
	document.getElementById("high_media_table").innerText = "$" + candle_estimators.high.media.toFixed(2);
	document.getElementById("high_media2_table").innerText = "$" + candle_estimators.high.mediaIter2.toFixed(2);
	document.getElementById("high_media3_table").innerText = "$" + candle_estimators.high.mediaIter3.toFixed(2);
	document.getElementById("high_delta_table").innerText = "$" + candle_estimators.high.delta.toFixed(2);
	document.getElementById("high_table").innerText = "$" + high.toFixed(2);
	
	// genera lines low
	generateLinesLow(candle_estimators.low, low)
	generateLinesHigh(candle_estimators.high, high);
	
	candle_estimators.low.mediaRef.applyOptions({
    axisLabelVisible: true});
}

function generateLinesLow(estimators, low){
	var listEstimators = [estimators.media, estimators.mediaIter2, estimators.mediaIter3, estimators.delta, low]
	var cotaSup = Math.max(...listEstimators) + 60
	var cotaInf = Math.min(...listEstimators) - 60
	
	var deltaMedia = cotaSup - estimators.media;
	var deltaMedia2 = cotaSup - estimators.mediaIter2;
	var deltaMedia3 = cotaSup - estimators.mediaIter3;
	var deltaMediaDelta = cotaSup - estimators.delta;
	var deltaLow = cotaSup - low;
	
	var complete = cotaSup - cotaInf;
	
	var porcentajeMedia = 100 - (( deltaMedia * 100) / complete );
	document.getElementById("low_media_table_progress").style.width = porcentajeMedia + "%";
	document.getElementById("low_media_delta_table").innerText =  "$" + (estimators.media - low ).toFixed(2); 
	
	var porcentajeMedia2 = 100 - (( deltaMedia2 * 100) / complete );
	document.getElementById("low_media2_table_progress").style.width = porcentajeMedia2 + "%";
	document.getElementById("low_media2_delta_table").innerText =  "$" + (estimators.mediaIter2 - low).toFixed(2);
	
	var porcentajeMedia3 = 100 - (( deltaMedia3 * 100) / complete );
	document.getElementById("low_media3_table_progress").style.width = porcentajeMedia3 + "%";
	document.getElementById("low_media3_delta_table").innerText =  "$" + (estimators.mediaIter3 - low).toFixed(2);
	
	var porcentajeDelta = 100 - (( deltaMediaDelta * 100) / complete );
	document.getElementById("low_delta_table_progress").style.width = porcentajeDelta + "%";
	document.getElementById("low_delta_delta_table").innerText =  "$" + (estimators.delta - low).toFixed(2);
	
	var porcentajeLow = 100 - (( deltaLow * 100) / complete );
	document.getElementById("low_table_progress").style.width = porcentajeLow + "%";
	
}

function generateLinesHigh(estimators, high){
	var listEstimators = [estimators.media, estimators.mediaIter2, estimators.mediaIter3, estimators.delta, high]
	var cotaSup = Math.max(...listEstimators) + 60;
	var cotaInf = Math.min(...listEstimators) - 60;
	
	var deltaMedia = estimators.media - cotaInf;
	var deltaMedia2 = estimators.mediaIter2 - cotaInf;
	var deltaMedia3 =  estimators.mediaIter3 - cotaInf;
	var deltaMediaDelta =  estimators.delta - cotaInf;
	var deltaHigh = high - cotaInf;
	
	var complete = cotaSup - cotaInf;
	
	var porcentajeMedia = ( deltaMedia * 100) / complete ;
	document.getElementById("high_media_table_progress").style.width = porcentajeMedia + "%";
	document.getElementById("high_media_delta_table").innerText =  "$" + (estimators.media - high ).toFixed(2); 
	
	var porcentajeMedia2 = ( deltaMedia2 * 100) / complete ;
	document.getElementById("high_media2_table_progress").style.width = porcentajeMedia2 + "%";
	document.getElementById("high_media2_delta_table").innerText =  "$" + (estimators.mediaIter2 - high).toFixed(2);
	
	var porcentajeMedia3 = ( deltaMedia3 * 100) / complete ;
	document.getElementById("high_media3_table_progress").style.width = porcentajeMedia3 + "%";
	document.getElementById("high_media3_delta_table").innerText =  "$" + (estimators.mediaIter3 - high).toFixed(2);
	
	var porcentajeDelta = ( deltaMediaDelta * 100) / complete ;
	document.getElementById("high_delta_table_progress").style.width = porcentajeDelta + "%";
	document.getElementById("high_delta_delta_table").innerText =  "$" + (estimators.delta - high).toFixed(2);
	
	var porcentajeHigh = ( deltaHigh * 100) / complete ;
	console.log(porcentajeHigh);
	document.getElementById("high_table_progress").style.width = porcentajeHigh + "%";
	
}


var AREA_MARKERS = [];

function updateOrders(lowTime, highTime){

	var orders = data.trades;
	var orderCandle = [];
	for(var i=0;i<orders.length;i++){
		if ((orders[i].buy.timestamp >= lowTime) && (orders[i].buy.timestamp <= highTime)){
			var color = 'green'
			if (orders[i].pnl < 0){
            	color = 'red'
			}
			orderCandle.push(
				{
					time: orders[i].buy.timestamp,
					position: 'aboveBar',
					color: color,
					shape: 'arrowDown',
					text: '$' + orders[i].buy.price,
				}
			);
			orderCandle.push(
				{
					time: orders[i].sell.timestamp,
					position: 'belowBar',
					color: color,
					shape: 'arrowUp',
					text: '$' + orders[i].sell.price,
				}
			);
		}
	}
	AREA_MARKERS = orderCandle;
	areaSeries.setMarkers(orderCandle);
}
var candle = null;

function updateCandleData(index){
	
	updateActualNextPrevIndex(index);
	
	// clear data
	clearChart();
	clearLogs();
	
	candle = data.candles[index];

	// subida exacerbada para entrenar
	setSubidaExacerbadaButton(candle);

	console.log(candle.date)
	document.getElementById("CandleDate").innerText = candle.date;

	// add ticks
	var bufferTicks = [];
	var bufferValues = [];
	var bufferTimes = [];

	for(var i=0; i < candle.ticks.length; i++){
		var tick = {time:candle.ticks[i].time, value:candle.ticks[i].value}
		bufferTicks.push(tick);
		bufferValues.push(candle.ticks[i].value);
		bufferTimes.push(candle.ticks[i].time);
	}
	
	//TODO agregar minimo, maximo, open, close al js
	var low = Math.min(...bufferValues);
	var high = Math.max(...bufferValues);

	var lowTime = Math.min(...bufferTimes);
	var highTime = Math.max(...bufferTimes);
	
	agregarTick(bufferTicks);

	updateEstimadores(candle.estimators, low, high);
	
	// update orders si existen
	updateOrders(lowTime, highTime);

	var log_candle_times = "Start: " + lowTime + " - End: " + highTime;
	agregarLogChart(log_candle_times, Date(Date.now()).toString());
	
	var logs = candle.logs;
	for (var i=0; i < logs.length; i++){
		agregarLogChart(logs[i].message, logs[i].date);
	}	// agrega logs

	// agrega line serie con los precios en promedio hechos en python
	createAverageLineSerie(candle.averageTicks);
	// var averageTicks = createAverageLineSerie(index, 15);
	createPendienteZeroAverageTicks(candle.inflectionPoints);
	
 /*

	// agrega estrategias de precio name, gananciaTotal, revenuePercent, indexStrategyPrice
	ocultarTodasEstrategiasPrecio();
	
	for(var i=0;i<candle.investStrategies.length;i++){
		var strategiePrice = candle.investStrategies[i];
		agregarEstrategiaPrecio(strategiePrice.name, strategiePrice.total, strategiePrice.profitPercent, i+1);
	}

	*/
	
	
}

function createAverageLineSerie(bufferTicks) {
	/*
	var candle = data.candles[index];
	var bufferTicks = [];
	var counter = 0;

	for(var i=0; i < candle.ticks.length; i++){
		counter = counter + 1;
		if (counter >= lags) {
			var acumValue = 0;
			for(var j= (i - (lags - 1)); j <= i; j++) {
				acumValue = acumValue + candle.ticks[j].value;
			}
			var mean = acumValue / lags;
			bufferTicks.push({time:candle.ticks[i].time, value:mean})
		}
	}
   */
	lineSeries.setData(bufferTicks);
}

function createPendienteZeroAverageTicks(ticks){

	for (var i =0; i < ticks.length;i++){
		AREA_MARKERS.push(
			{
				time: ticks[i].time,
				position: 'aboveBar',
				color: "blue",
				shape: 'circle',
				text: ''
			}
		);
	}
	areaSeries.setMarkers(AREA_MARKERS);
}

function updateActualNextPrevIndex(index){
	ACTUALINDEX = index;
	NEXTINDEX = ACTUALINDEX + 1;
	if (NEXTINDEX >= data.candles.length){
		NEXTINDEX = NEXTINDEX -1;
	};
	PREVINDEX = ACTUALINDEX - 1;
	if (PREVINDEX < 0){
		PREVINDEX = 0;
	}
}

function goNext(){
	updateCandleData(NEXTINDEX);
}

function goPrev(){
	updateCandleData(PREVINDEX);
}

function checkCandleTicksLength(dataset){
	var length = dataset.candles.length;
	var totalLength = 0;
	for(var i = 0;i<length;i++){
		totalLength =  totalLength + dataset.candles[i].ticks.length
	}
	console.log("Media ticks por vela:")
	console.log(totalLength/dataset.candles.length)

}

function logFirstLastTicksTime(dataset){
   var length = dataset.candles.length;
   var first = dataset.candles[0].ticks[0].time;
   console.log("-----------------------------");
   console.log("Fecha primer candle es:");
   console.log(dataset.candles[0].date);
   console.log("Primer tick time es:");
   console.log(first);
   var last = dataset.candles[length-1].ticks[dataset.candles[length-1].ticks.length -1].time;
   console.log("Segundo tick time es:");
   console.log(last);

   console.log("Fecha ultimo candle es:");
   console.log(dataset.candles[length-1].date);
   console.log("-----------------------------")
}

/*
  Esta funcion genera en consola la data de un csv para poder entrenar la red nueronal de clasificacion.
  El clasificado se hace de forma manual, en este caso se buscan los patrones de 'subida exaservada'.
*/
function setSubidaExacerbadaButton(candle){
	var element = document.getElementById("subidaExacerbadaButton");
	if (candle["sbuidaExacerbada"] == 1){
		element.style.backgroundColor = "green";

	} else {
		element.style.backgroundColor = "red";
	}
}
function createCSVDataEtiquetadoManualSubidaExacerbada(){
	var TICKS_TO_ADD = 30;
	var CSV = "";
	var CSV_LINE = "";
	// para cada uno de los candles
	var candles = data.candles;
	var length = candles.length;
	var totalSubidasExacerbadas = 0;
	for(var i=0; i < length;i++){
		CSV_LINE = "";
		// toma los datos de los primeros X ticks
		var candle = candles[i];
		var ticks = candle.ticks;
		if (ticks.length >= 30){		
			for (var j=0; j < TICKS_TO_ADD; j++){
				CSV_LINE = CSV_LINE + ticks[j].value + ",";
			}
			// toma los estimadores low
			var estimators = candle.estimators;
			CSV_LINE = CSV_LINE + estimators.low.media + "," + estimators.low.mediaIter2 + "," + estimators.low.mediaIter3 + "," + estimators.low.delta;
			// toma los estimadores high
			CSV_LINE = CSV_LINE + "," + estimators.high.media + "," + estimators.high.mediaIter2 + "," + estimators.high.mediaIter3 + "," + estimators.high.delta;
			// si en el candle no existe subidaExacerbada pone False, si existe true pone True 
			if (candle["sbuidaExacerbada"] == 1){
				CSV_LINE = CSV_LINE + "," + "1\n";
				totalSubidasExacerbadas = totalSubidasExacerbadas + 1;
			} else {
				CSV_LINE = CSV_LINE + "," + "0\n";
			}
			CSV = CSV + CSV_LINE;
		} else {
			console.log("Esta vela tiene " + ticks.length + " no se agrega");
		} 
	}
	console.log(CSV);
	alert("CSV ready in console!");
	console.log("El total de subidas exacerbads es " + totalSubidasExacerbadas);
	console.log("Se puede decir q en promedio hay una subida exacerbada cada " + (totalSubidasExacerbadas/length));
	//format
	// price1,... price30, low_media, low_media_iter2,low_media_iter3,low_delta,high_media, high_media_iter2, high_media_iter3,high_delta, subida_exa
}

function subidaExacerbada(element){
	var candle = data.candles[ACTUALINDEX];
	if (candle["sbuidaExacerbada"] == 1){
		candle["sbuidaExacerbada"] = 0;
		element.style.backgroundColor = "red";
		alert("Se cambio propiedad subida exacerbada a 0!");

	} else {
		element.style.backgroundColor = "green";
		candle["sbuidaExacerbada"] = 1;
		alert("Se cambio propiedad subida exacerbada a 1!");
	}
}

function checkTouchLowEstimators(value, candle_estimators){
	if (value <= candle_estimators.low.media){
		return true;
	}
 	if (value <= candle_estimators.low.mediaIter2){
		 return true;
	 }
	 if (value <= candle_estimators.low.mediaIter3){
		return true;
	}
	if (value <= candle_estimators.low.delta){
		return true;
	}
	return false;
	
}

function checkTouchHighEstimators(value, candle_estimators){
	if (value <= candle_estimators.high.media){
		return true;
	}
 	if (value <= candle_estimators.high.mediaIter2){
		 return true;
	 }
	 if (value <= candle_estimators.high.mediaIter3){
		return true;
	}
	if (value <= candle_estimators.high.delta){
		return true;
	}
	return false;
	
}

function checkPassHighEstimators(ticks, MAX_TICKS, candle_estimators){
	var low_value = ticks[0].value;
	for(var i=0;i<MAX_TICKS;i++){
		if (ticks[i].value < low_value){
			low_value = ticks[i].value;
		}		
	}
	if (low_value >= candle_estimators.high.media){
		return false;
	}
 	if (low_value >= candle_estimators.high.mediaIter2){
		 return false;
	 }
	 if ( low_value >= candle_estimators.high.mediaIter3){
		return false;
	}
	/*if (low_value >= candle_estimators.high.delta){
		return false;
	}*/
	return true;
}
// console.log(createCSVDataEtiquetadoManualSubidaExacerbada(data));
function testStrategy() {
	
	var MAX_TICKS = 6;
	var MINIMO_INDEX = 5;
	var candles = data.candles;
	var length = candles.length;
	var totalSubidasExacerbadas = 0;
	
	for(var i=0; i < length;i++){
		var candle = candles[i];
		//var candle = data.candles[ACTUALINDEX];
		var ticks = candle.ticks;
		// toma los datos de los primeros X ticks
		if (ticks.length > MAX_TICKS){
			for (var j=0;j<MAX_TICKS;j++){
				// si toco algun estimador low literal en los primeros 12, no se ejecuta
				// si alguno de los estimadores low es mayor o igual q el valor, retorna false
				if (checkTouchLowEstimators(ticks[j].value, candle.estimators)) {
					candle["sbuidaExacerbada"] = 0;
					break;
				}

				
			}
		}

		// si no toco algun estimador high primeros MINIMO_INDEX, no se ejecuta.
		// si alguno de los estimadores low es mayor o igual q el valor, retorna false
		if (checkTouchHighEstimators(ticks[MINIMO_INDEX].value, candle.estimators)) {
			candle["sbuidaExacerbada"] = 0;
		}

		// si alguno de los estimadores nunca fue alcanzado no se contabiliza
		// puede ser que se permita el delta, pero las subidas exacervadas en su mayoria toman los cuatros
		if (!checkPassHighEstimators(ticks, MAX_TICKS, candle.estimators)){
			candle["sbuidaExacerbada"] = 0;
		}
	}

	for(var i=0; i < length;i++){
		var candle = candles[i];
		if(candle["sbuidaExacerbada"] == 1){
			totalSubidasExacerbadas = totalSubidasExacerbadas + 1;
		}
	}
	console.log(" total " + totalSubidasExacerbadas);
}

checkCandleTicksLength(data);
logFirstLastTicksTime(data);
refreshDashBoard(data);
// testStrategy(data);