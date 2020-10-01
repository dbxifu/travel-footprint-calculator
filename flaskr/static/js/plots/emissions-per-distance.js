function draw_emissions_per_distance(divSelector, csvUrl) {
    // set the dimensions and margins of the graph
    let margin = {top: 48, right: 88, bottom: 68, left: 98},
        width = 960 - margin.left - margin.right,
        height = 540 - margin.top - margin.bottom;

    const sliceThickness = 500.0;


    function getTicks(maxValue, interval, startValue = 0) {
        let range = [];
        for (let i = startValue; i <= maxValue; i += interval) {
            range.push(i);
        }
        return range;
    }

    function getBottomTicks(maxDistance) {
        let range = getTicks(maxDistance, 2500, 2500);
        range.push(500);
        return range;
    }

    function getLeftTicks(maxemissions) {
        return getTicks(maxemissions, Math.floor((maxemissions / 8) / 1000) * 1000);
    }

    function getRightTicks(maxemissionsPercent) {
        return getTicks(maxemissionsPercent, 2);
    }

    function getAttendeesAmountOnRight(sliceId, attendeeNumberPerGroup) {
        let attendeesAmount = 0;
        let sliceInt = Math.floor(sliceId);
        let sliceFloat = sliceId - sliceInt;
        for (let i = sliceInt; i < attendeeNumberPerGroup.length; i++) {
            attendeesAmount += attendeeNumberPerGroup[i] * (1 - sliceFloat);
            sliceFloat = 0;
        }
        return attendeesAmount;

    }

    function setupCursorBoxes(event, attendeeSum, attendeeNumberPerGroup, xScale, tooltip, vertical, rightArea) {
        const x = d3.pointer(event)[0];
        const y = d3.pointer(event)[1];
        // var y = d3.event.pageY - document.getElementById(<id-of-your-svg>).getBoundingClientRect().y + 10
        // x += 5;

        // console.log("Mouse move", x, y);

        vertical.style("left", x + "px");
        rightArea.style("left", x + "px");
        rightArea.style("width", (width+margin.left-x) + "px");
        tooltip.style("left", (x + 10) + "px");
        tooltip.style("top", (y - 20) + "px");

        // let sliceId = xScale.invert(x - d3.selectAll("g.yl.axis")._groups[0][0].getBoundingClientRect().right) / 500;

        let sliceId = xScale.invert(x - margin.left) / sliceThickness;

        // console.log(`Slice ${sliceId} under the mouse.`);

        // let sliceId = xScale.invert(x * 1.025 - d3.selectAll("g.yl.axis")._groups[0][0].getBoundingClientRect().x- margin.left)/500 +1;
        let attendeePercent = (getAttendeesAmountOnRight(sliceId, attendeeNumberPerGroup) / attendeeSum * 100.0).toFixed(1);
        if (
            x < margin.left
            ||
            x > width + margin.left
            ||
            y < margin.top
            ||
            y > height + margin.top
        ) {
            rightArea.style("width", 0);
            vertical.style("width", 0);
            tooltip.style("display", "none");
        }
        else {
            rightArea.style("width", d3.selectAll("g.yr.axis")._groups[0][0].getBoundingClientRect().x - x);
            vertical.style("width", "2px");
            tooltip.style("display", "inherit");
        }
        tooltip.text(attendeePercent + " % of attendees");
        // console.log(d3.selectAll("g.x.axis")._groups[0][0]);
        // console.log(d3.selectAll("g.x.axis")._groups[0][0].getBoundingClientRect().x);
    }

    function addVerticalLineAndListenCursor(xScale, attendeeNumberPerGroup, attendeeSum) {
        let verticalRuler = d3.select(divSelector)
            .append("div")
            // .attr("class", "remove")
            .style("position", "absolute")
            .style("z-index", "19")
            .style("width", "2px")
            .style("height", (height) + "px")
            .style("top", (margin.top) + "px")
            .style("bottom", "30px")
            .style("left", "-10px")
            .style("background", "#000");

        let rightArea = d3.select(divSelector)
            .append("div")
            // .attr("class", "remove")
            .style("position", "absolute")
            .style("z-index", "-50")
            .style("width", "0px")
            .style("height", (height) + "px")
            .style("top", (margin.top) + "px")
            .style("bottom", "30px")
            .style("left", "0px")
            .style("background", "rgba(60, 200, 60, 0.3)");

        let tooltip = d3.select(divSelector)
            .append("div")
            .attr("class", "no-pointer-events")
            .style("display", "none")
            .style("position", "absolute")
            .style("z-index", "20")
            .style("width", "150px")
            .style("height", "22px")
            .style("top", "10px")
            .style("bottom", "30px")
            .style("left", "0px")
            .style("border", "1px solid grey")
            .style("background", "rgba(255, 255, 255, 0.7)");

        d3.select(divSelector + " svg")
            .on("mousemove", function (event) {
                setupCursorBoxes(event, attendeeSum, attendeeNumberPerGroup, xScale, tooltip, verticalRuler, rightArea);
            })
            .on("mouseover", function (event) {
                setupCursorBoxes(event, attendeeSum, attendeeNumberPerGroup, xScale, tooltip, verticalRuler, rightArea);
            });
    }

    document.addEventListener("DOMContentLoaded", () => {
        let maxemissions = 0;
        let maxemissionsPercent = 0;
        let maxDistance = 0;
        let svg = d3.select(divSelector)
            .append("svg")
            // .attr("id", divSelector + "-svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        let emissionsPerGroup = [];
        let attendeeNumberPerGroup = [];
        let emissionsSum = 0;
        let attendeeSum = 0;
        let rows = [];

        const on_csv_datum = function (datum) {
            let trainAttendee = parseInt(datum["train trips_amount"]);
            let planeAttendee = parseInt(datum["plane trips_amount"]);
            if (trainAttendee === 0 && planeAttendee === 0) {
                return;
            }
            let attendeeNumber = trainAttendee + planeAttendee;
            let distance_km = datum.distance_km / attendeeNumber;
            let co2_kg = parseFloat(datum.co2_kg);
            if (co2_kg === "NaN" || distance_km / 500 > 37 || distance_km === "NaN") {
                return;
            }
            rows.push(datum);
            maxDistance = Math.max(maxDistance, distance_km);
            emissionsSum += co2_kg;

        };

        const on_csv_ready = function () {
            for (let i = 0; i <= maxDistance / 500; i++) {
                emissionsPerGroup[i] = 0;
                attendeeNumberPerGroup[i] = 0;
            }
            rows.forEach((element, index) => {
                let trainAttendee = parseInt(element["train trips_amount"]);
                let planeAttendee = parseInt(element["plane trips_amount"]);
                let attendeeNumber = trainAttendee + planeAttendee;
                let distance_km = element.distance_km / attendeeNumber;
                let co2_kg = parseFloat(element.co2_kg);
                emissionsPerGroup[Math.floor(distance_km / 500)] += parseFloat(co2_kg);
                attendeeNumberPerGroup[Math.floor(distance_km / 500)] += attendeeNumber;
                attendeeSum += attendeeNumber;
            });
            emissionsPerGroup.forEach((element, index) => {
                maxemissions = Math.max(maxemissions, element);
                maxemissionsPercent = Math.max(maxemissionsPercent, element / emissionsSum * 100.0)
            });
            maxDistance += 2000;
            // console.log(maxDistance);

            // Title
            svg.append("text")
                .attr("transform",
                    "translate(" + (0) + ", -18)")
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
                .domain([0, maxemissions])
                .range([height, 0]);
            let ylAxis = d3.axisLeft(yl)
                .tickValues(getLeftTicks(maxemissions));
            svg.append("g")
                .attr("class", "yl axis")
                .call(ylAxis);

            // Y axis Right
            let yr = d3.scaleLinear()
                .domain([0, maxemissionsPercent])
                .range([height, 0]);
            let yrAxis = d3.axisRight(yr)
                .tickValues(getRightTicks(maxemissionsPercent));
            svg.append("g")
                .attr("transform", "translate(" + width + ", 0)")
                .attr("class", "yr axis")
                .call(yrAxis);

            svg.append("text")
                .attr("transform",
                    "translate(" + (width / 2) + " ," +
                    (height + margin.top + 2) + ")")
                .style("text-anchor", "middle")
                .text("Distance travelled (km)");

            svg.append("text")
                .attr("transform",
                    "translate(" + (width) + ", 0), rotate(-90)")
                .attr("x", 0 - (height / 2))
                .attr("y", 13 + margin.right / 2.0)
                .style("text-anchor", "middle")
                .text("Share of emission (%)");

            svg.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - (5 * margin.left / 6.0))
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .text("Emission (kgCO2e)");
            // set the parameters for the histogram
            const histogram = d3.histogram()
                .domain(x.domain())  // then the domain of the graphic
                .thresholds(x.ticks(Math.floor(maxDistance / 500))); // then the numbers of bins

            let histolol = histogram(0);
            // console.log(histolol);
            let barSettings = [];
            emissionsPerGroup.forEach((element, index) => {
                barSettings[index] =
                    {
                        height: element,
                        leftBorder: histolol[index].x0,
                        rightBorder: histolol[index].x1,
                    };
                // console.log(index);
                // console.log(barSettings[index]);
            });
            svg.selectAll("rect")
                .data(barSettings)
                .enter()
                .append("rect")
                .attr("x", 1)
                .attr("transform", function (d) {
                    return "translate(" + x(d.leftBorder) + "," + yl(d.height) + ")";
                })
                .attr("width", function (d) {
                    return x(d.rightBorder) - x(d.leftBorder) - 1;
                })
                .attr("height", function (d) {
                    return (height - yl(d.height));
                })
                .style("z-index", "500")
                .style("fill", "#4444E5");
            addVerticalLineAndListenCursor(x, attendeeNumberPerGroup, attendeeSum);
        };

        d3.csv(csvUrl, on_csv_datum)
            .then(on_csv_ready);
    });

}