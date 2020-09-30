// set the dimensions and margins of the graph
let margin = {top: 30, right: 62, bottom: 62, left: 72},
    width = 960 - margin.left - margin.right,
    height = 540 - margin.top - margin.bottom;

let divId = "chart-container";

function getTicks(maxValue, interval, startValue=0)
{
    let range = [];
    for (let i = startValue ; i <= maxValue ; i+=interval)
    {
        range.push(i);
    }
    return range;
}

function getBottomTicks(maxDistance) {
    let range = getTicks(maxDistance, 2500, 2500);
    range.push(500);
    return range;
}

function getLeftTicks(maxEmission) {
    return getTicks(maxEmission, Math.floor((maxEmission / 8) / 1000)* 1000) ;
}

function getRightTicks(maxEmissionPercent) {
    return getTicks(maxEmissionPercent, 2);
}

function getAttendeeOnRight(sliceId, attendeeNumberPerGroup)
{
    let attendeeSum = 0;
    let sliceInt = Math.floor(sliceId);
    let sliceFloat = sliceId - sliceInt;
    for(let i = sliceInt; i < attendeeNumberPerGroup.length; i++)
    {
        attendeeSum += attendeeNumberPerGroup[i] * (1 - sliceFloat);
        sliceFloat = 0;
    }
    return attendeeSum;

}

function setupCursorBoxes(event, attendeeSum, attendeeNumberPerGroup, xScale, box, vertical, rightArea)
{
    // mousex = d3.mouse(this);
    var x = d3.pointer(event)[0];
    var y = d3.pointer(event)[1];
    // var y = d3.event.pageY - document.getElementById(<id-of-your-svg>).getBoundingClientRect().y + 10
    // x += 5;
    vertical.style("left", x + "px" );
    rightArea.style("left", x + "px" );
    box.style("left", (x + 10) + "px");
    box.style("top", (y - 20) + "px");
    let sliceId = xScale.invert(x - d3.selectAll("g.yl.axis")._groups[0][0].getBoundingClientRect().right)/500;
    // let sliceId = xScale.invert(x * 1.025 - d3.selectAll("g.yl.axis")._groups[0][0].getBoundingClientRect().x- margin.left)/500 +1;
    let attendeePercent = (getAttendeeOnRight(sliceId, attendeeNumberPerGroup) / attendeeSum * 100.0).toFixed(1);
    if(x > d3.selectAll("g.yr.axis")._groups[0][0].getBoundingClientRect().x ||
        x < d3.selectAll("g.yl.axis")._groups[0][0].getBoundingClientRect().right)
    {
        rightArea.style("width", 0);
        vertical.style("width", 0);
        box.style("display", "none");
    }
    else
    {
        rightArea.style("width", d3.selectAll("g.yr.axis")._groups[0][0].getBoundingClientRect().x - x );
        vertical.style("width", "2px");
        box.style("display", "inherit");
    }
    box.text(attendeePercent + " % of attendees");
    box.text(attendeePercent + " % of attendees");
    // console.log(d3.selectAll("g.x.axis")._groups[0][0]);
    // console.log(d3.selectAll("g.x.axis")._groups[0][0].getBoundingClientRect().x);
}

function addVerticalLineAndListenCursor(xScale, attendeeNumberPerGroup, attendeeSum) {
    let vertical = d3.select("#" + divId)
        .append("div")
        .attr("class", "remove")
        .style("position", "absolute")
        .style("z-index", "19")
        .style("width", "2px")
        .style("height", (height) + "px")
        .style("top", (10 + margin.top) + "px")
        .style("bottom", "30px")
        .style("left", "0px")
        .style("background", "#000");

    let rightArea = d3.select("#" + divId)
        .append("div")
        .attr("class", "remove")
        .style("position", "absolute")
        .style("z-index", "-50")
        .style("width", "2000px")
        .style("height", (height) + "px")
        .style("top", (10 + margin.top) + "px")
        .style("bottom", "30px")
        .style("left", "0px")
        .style("background", "rgba(60, 200, 60, 0.3)");


    let box = d3.select("#" + divId)
        .append("div")
        .attr("class", "remove")
        .style("position", "absolute")
        .style("z-index", "20")
        .style("width", "150px")
        .style("height", "22px")
        .style("top", "10px")
        .style("bottom", "30px")
        .style("left", "0px")
        .style("border", "1px solid grey")
        .style("background", "rgba(255, 255, 255, 0.7)");
    d3.select("#" + divId)
        .on("mousemove", function(event){
            setupCursorBoxes(event, attendeeSum, attendeeNumberPerGroup, xScale, box, vertical, rightArea);
        })
        .on("mouseover", function(event){
            setupCursorBoxes(event, attendeeSum, attendeeNumberPerGroup, xScale, box, vertical, rightArea);

        });
}


document.onreadystatechange = () => {
    if (document.readyState === 'complete') {
        let maxEmission = 0;
        let maxEmissionPercent = 0;
        let maxDistance = 0;
        let svg = d3.select("#" + divId)
            .append("svg")
            .attr("id", "graph-svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        let emissionPerGroup = [];
        let attendeeNumberPerGroup = [];
        let emissionSum = 0;
        let attendeeSum = 0;
        let rows = [];


        d3.csv("2020-09-30_04_21_19_87a1.csv", function (data) {
            let trainAttendee = parseInt(data["train trips_amount"]);
            let planeAttendee = parseInt(data["plane trips_amount"]);
            if(trainAttendee === 0 && planeAttendee === 0)
            {
                return;
            }
            let attendeeNumber = trainAttendee + planeAttendee;
            let distance_km = data.distance_km / attendeeNumber;
            let co2_kg = parseFloat(data.co2_kg);
            if (co2_kg === "NaN" || distance_km/500 > 37 || distance_km === "NaN")
            {
                return;
            }
            rows.push(data);
            maxDistance = Math.max(maxDistance, distance_km);
            emissionSum += co2_kg;
        }).then((() => {
            for (let i = 0; i <= maxDistance/500; i++)
            {
                emissionPerGroup[i] = 0;
                attendeeNumberPerGroup[i] = 0;
            }
            rows.forEach((element, index) => {
                let trainAttendee = parseInt(element["train trips_amount"]);
                let planeAttendee = parseInt(element["plane trips_amount"]);
                let attendeeNumber = trainAttendee + planeAttendee;
                let distance_km = element.distance_km / attendeeNumber;
                let co2_kg = parseFloat(element.co2_kg);
                emissionPerGroup[Math.floor(distance_km/500)] += parseFloat(co2_kg);
                attendeeNumberPerGroup[Math.floor(distance_km/500)] += attendeeNumber;
                attendeeSum += attendeeNumber;
            });
            emissionPerGroup.forEach((element, index) => {
                maxEmission = Math.max(maxEmission, element);
                maxEmissionPercent = Math.max(maxEmissionPercent, element / emissionSum * 100.0)
            });
            maxDistance += 2000;
            // console.log(maxDistance);

            //Title
            svg.append("text")
                .attr("transform",
                    "translate(" + (70 + margin.left)  + ", -12)")
                .style("text-anchor", "middle")
                .style("font-weight", "bold")
                .style("font-size", "130%")
                .text("Emissions per distance");

            // X axis: scale and draw:
            let x = d3.scaleLinear()
                .domain([0, maxDistance])
                .range([0, width]);
            let xAxis = d3.axisBottom(x)
                .tickValues(getBottomTicks(maxDistance));
            svg.append("g")
                .attr("transform", "translate(0," + height + ")")
                .attr("class", "x axis")
                .call(xAxis);
            d3.selectAll("g.x.axis")
                .selectAll(".tick")
                .filter(function (d) {
                    return d === 0;
                })
                .remove();

            // Y axis Left
            let yl = d3.scaleLinear()
                .domain([0, maxEmission])
                .range([height, 0]);
            let ylAxis = d3.axisLeft(yl)
                .tickValues(getLeftTicks(maxEmission));
            svg.append("g")
                .attr("class", "yl axis")
                .call(ylAxis);

            // Y axis Right
            let yr = d3.scaleLinear()
                .domain([0, maxEmissionPercent])
                .range([height, 0]);
            let yrAxis = d3.axisRight(yr)
                .tickValues(getRightTicks(maxEmissionPercent));
            svg.append("g")
                .attr("transform", "translate(" + width + ", 0)")
                .attr("class", "yr axis")
                .call(yrAxis);

            svg.append("text")
                .attr("transform",
                    "translate(" + (width/2) + " ," +
                    (height + margin.top + 12) + ")")
                .style("text-anchor", "middle")
                .text("Distance travelled (km)");

            svg.append("text")
                .attr("transform",
                    "translate(" + (width)  + ", 0), rotate(-90)")
                .attr("x",0 - (height / 2))
                .attr("y", 42)
                .style("text-anchor", "middle")
                .text("Share of emission [%]");

            svg.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left)
                .attr("x",0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .text("Emission (tCO2e)");
            // set the parameters for the histogram
            var histogram = d3.histogram()
                .domain(x.domain())  // then the domain of the graphic
                .thresholds(x.ticks(Math.floor(maxDistance/500))); // then the numbers of bins

            let histolol = histogram(0);
            // console.log(histolol);
            let barSettings = [];
            emissionPerGroup.forEach((element, index) => {
                barSettings[index]=
                {
                    height : element,
                    leftBorder : histolol[index].x0,
                    rightBorder : histolol[index].x1,
                };
                // console.log(index);
                // console.log(barSettings[index]);
            });
            svg.selectAll("rect")
                .data(barSettings)
                .enter()
                .append("rect")
                .attr("x", 1)
                .attr("transform", function(d) { return "translate(" + x(d.leftBorder) + "," + yl(d.height) + ")"; })
                .attr("width", function(d) { return x(d.rightBorder) - x(d.leftBorder) -1 ; })
                .attr("height", function(d) { return (height-yl(d.height)); })
                .style("z-index", "500")
                .style("fill", "#4444E5");
            addVerticalLineAndListenCursor(x, attendeeNumberPerGroup, attendeeSum);
        }));

    }
};