function draw_sorted_emissions_inequality(containerSelector, csvUrl) {

    // set the dimensions and margins of the graph
    let margin = {top: 30, right: 10, bottom: 62, left: 72},
        width = 600 - margin.left - margin.right,
        height = 700 - margin.top - margin.bottom;

    function getTicks(maxValue, interval, startValue = 0) {
        let range = [];
        for (let i = startValue; i <= maxValue; i += interval) {
            range.push(i);
        }
        return range;
    }

    function getBottomTicks(maxAttendeePercent) {
        return getTicks(maxAttendeePercent, 20);
    }

    function getLeftTicks(maxemissionsPercent) {
        return getTicks(maxemissionsPercent, 20);
    }

    function getSliceCollision(x, y, barSettings) {
        let result = false;
        barSettings.forEach((element, index) => {
            if (x < element.rightBorder && x > element.leftBorder) {
                let binYDiff = element.topBorder - element.bottomBorder;
                let binXDiff = element.rightBorder - element.leftBorder;
                let binDiagonalAngle = Math.atan2(binYDiff, binXDiff);
                // let binYCenter = (element.topBorder + element.bottomBorder)/2;
                // let binXCenter = (element.rightBorder + element.leftBorder)/2;
                let mouseXDiff = element.rightBorder - x;
                let mouseYDiff = element.topBorder - y;
                let mouseToCenterAngle = Math.atan2(mouseYDiff, mouseXDiff);
                // console.log(binDiagonalAngle);
                // console.log(mouseToCenterAngle);

                if (mouseToCenterAngle < binDiagonalAngle) {
                    barSettings.forEach((element, index) => {
                        if (y < element.topBorder && y > element.bottomBorder) {
                            let lb = barSettings[index].leftBorder;
                            let rb = barSettings[index].rightBorder;
                            let tb = barSettings[index].topBorder;
                            let bb = barSettings[index].bottomBorder;
                            let binCollisionRatio = (y - bb) / (tb - bb);
                            let otherAxisLevel = (rb - lb) * binCollisionRatio + lb;
                            result = {
                                binDiagonalAngle: binDiagonalAngle,
                                isXDriving: false,
                                binIndex: index,
                                otherAxisLevel: otherAxisLevel
                            };

                        }
                    });


                }
                else {
                    let lb = barSettings[index].leftBorder;
                    let rb = barSettings[index].rightBorder;
                    let tb = barSettings[index].topBorder;
                    let bb = barSettings[index].bottomBorder;
                    let binCollisionRatio = (x - lb) / (rb - lb);
                    let otherAxisLevel = (tb - bb) * binCollisionRatio + bb;
                    // console.log(otherAxisLevel);
                    result = {
                        binDiagonalAngle: binDiagonalAngle,
                        isXDriving: true,
                        binIndex: index,
                        otherAxisLevel: otherAxisLevel
                    }
                }
            }
        });
        return result;

    }

    function setupCursorBoxes(event, xScale, yScale, barSettings, vertical, horizontal, tooltip) {
        const x = d3.pointer(event)[0];
        const y = d3.pointer(event)[1];
        // var y = d3.event.pageY - document.getElementById(<id-of-your-svg>).getBoundingClientRect().y + 10
        tooltip.style("left", (x + 10) + "px");
        tooltip.style("top", (y - 30) + "px");
        let xInGraph = xScale.invert(x - margin.left);
        let yInGraph = yScale.invert(y - margin.top);

        // let sliceId = xScale.invert(x * 1.025 - d3.selectAll("g.yl.axis")._groups[0][0].getBoundingClientRect().x- margin.left)/500 +1;
        // let attendeePercent = (getAttendeeOnRight(sliceId, attendeeNumberPerGroup) / attendeeSum * 100.0).toFixed(1);
        if (
            x < margin.left
            ||
            x > width + margin.left
            ||
            y < margin.top
            ||
            y > height + margin.top
    ) {
            vertical.style("display", "none");
            horizontal.style("display", "none");
            tooltip.style("display", "none");
        }
        else {
            vertical.style("display", "inherit");
            horizontal.style("display", "inherit");
            tooltip.style("display", "inherit");
            let sliceCollision = getSliceCollision(xInGraph, yInGraph, barSettings);
            // console.log(sliceCollision);
            if (sliceCollision) {

                if (sliceCollision.isXDriving) {
                    vertical.style("left", x + "px");
                    horizontal.style("top", yScale(sliceCollision.otherAxisLevel) + margin.top + "px");

                    tooltip.text(Math.round(xInGraph) + "% of participants emitted " + Math.round(sliceCollision.otherAxisLevel) + "% of CO\u2082eq");
                } else {
                    horizontal.style("top", y + "px");
                    vertical.style("left", xScale(sliceCollision.otherAxisLevel) + margin.left + "px");

                    // noinspection JSSuspiciousNameCombination o.O
                    tooltip.text(Math.round(100.0 - sliceCollision.otherAxisLevel) + "% of participants emitted " + Math.round(100.0 - yInGraph) + "% of CO\u2082eq");
                    // tooltip.text(sliceCollision.otherAxisLevel + " " + yInGraph);
                }
            }

        }
        // tooltip.text(attendeePercent + " % of attendees");
        // console.log(d3.selectAll("g.x.axis")._groups[0][0]);
        // console.log(d3.selectAll("g.x.axis")._groups[0][0].getBoundingClientRect().x);
    }

    function addVerticalLineAndListenCursor(xScale, yScale, barSettings) {
        let vertical = d3.select(containerSelector)
            .append("div")
            .attr("class", "no-pointer-events")
            .style("display", "none")
            .style("position", "absolute")
            .style("z-index", "19")
            .style("width", "2px")
            .style("height", (height) + "px")
            .style("top", (margin.top) + "px")
            .style("bottom", "30px")
            .style("left", "0px")
            .style("background", "#000");

        let horizontal = d3.select(containerSelector)
            .append("div")
            .attr("class", "no-pointer-events")
            .style("display", "none")
            .style("position", "absolute")
            .style("z-index", "19")
            .style("width", (width) + "px")
            .style("height", "2px")
            .style("top", "0px")
            .style("bottom", "30px")
            .style("left", (margin.left) + "px")
            .style("background", "#000");

        let tooltip = d3.select(containerSelector)
            .append("div")
            .attr("class", "no-pointer-events")
            .style("display", "none")
            .style("position", "absolute")
            .style("z-index", "20")
            .style("width", "230px")
            .style("height", "60px")
            .style("top", "10px")
            .style("bottom", "30px")
            .style("left", "0px")
            .style("padding", "7px 10px")
            .style("border", "1px solid grey")
            .style("background", "rgba(255, 255, 255, 0.7)");

        d3.select(containerSelector)
            .on("mousemove", function (event) {
                setupCursorBoxes(event, xScale, yScale, barSettings, vertical, horizontal, tooltip);
            })
            .on("mouseover", function (event) {
                setupCursorBoxes(event, xScale, yScale, barSettings, vertical, horizontal, tooltip);
            });
    }


    document.addEventListener("DOMContentLoaded", () => {
        width = Math.max(880, $(containerSelector).parent().width());
        width = width - margin.left - margin.right;
        let maxAttendeePercent = 100;
        let maxEmissionsPercent = 100;
        let svg = d3.select(containerSelector)
            .append("svg")
            .attr("id", "graph-svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        let emissionsPerGroup = [];
        let attendeeNumberPerGroup = [];
        let emissionsSum = 0;
        let attendeeSum = 0;
        let data = [];
        d3.csv(csvUrl, function (datum) {
            let trainAttendee = parseInt(datum["train trips_amount"]);
            let planeAttendee = parseInt(datum["plane trips_amount"]);
            if (trainAttendee === 0 && planeAttendee === 0) {
                return;
            }
            let attendeeNumber = trainAttendee + planeAttendee;
            let distance_km = datum.distance_km / attendeeNumber;
            let co2_kg = parseFloat(datum.co2_kg);
            if (co2_kg === "NaN" || distance_km === "NaN") {
                return;
            }
            data.push(datum);
        }).then((() => {
            data.forEach((datum, index) => {
                let trainAttendee = parseInt(datum["train trips_amount"]);
                let planeAttendee = parseInt(datum["plane trips_amount"]);
                let attendeeNumber = trainAttendee + planeAttendee;
                datum["emissions_per_capita"] = parseFloat(datum.co2_kg) / attendeeNumber;
            });

            data.sort(function (a, b) {
                if (a.emissions_per_capita > b.emissions_per_capita) {
                    return 1;
                }
                if (b.emissions_per_capita > a.emissions_per_capita) {
                    return -1;
                }
                return 0;
            });
            console.log(data);
            let dataIndex = 0;
            data.forEach((datum, index) => {
                let trainAttendee = parseInt(datum["train trips_amount"]);
                let planeAttendee = parseInt(datum["plane trips_amount"]);
                let attendeeNumber = trainAttendee + planeAttendee;
                let co2_kg = parseFloat(datum.co2_kg);
                emissionsSum += co2_kg;
                attendeeSum += attendeeNumber;
                emissionsPerGroup[dataIndex] = emissionsSum;
                attendeeNumberPerGroup[dataIndex] = attendeeSum;
                dataIndex += 1;
            });
            // emissionsPerGroup.forEach((element, index) => {
            //     maxemissions = Math.max(maxemissions, element);
            //     maxemissionsPercent = Math.max(maxemissionsPercent, element / emissionsSum * 100.0)
            // });
            // maxDistance += 2000;
            // console.log(maxDistance);

            //Title
            svg.append("text")
                .attr("transform",
                    "translate(" + (70 + margin.left) + ", -12)")
                .style("text-anchor", "middle")
                .style("font-weight", "bold")
                .style("font-size", "130%")
                .text("Sorted carbon emissions");

            // X axis: scale and draw:
            let x = d3.scaleLinear()
                .domain([0, maxAttendeePercent])
                .range([0, width]);
            let xAxis = d3.axisBottom(x)
                .tickValues(getBottomTicks(maxAttendeePercent));
            svg.append("g")
                .attr("transform", "translate(0," + height + ")")
                .attr("class", "x axis")
                .call(xAxis);

            // Y axis Left
            let y = d3.scaleLinear()
                .domain([0, maxEmissionsPercent])
                .range([height, 0]);
            let yAxis = d3.axisLeft(y)
                .tickValues(getLeftTicks(maxEmissionsPercent));
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            svg.append("text")
                .attr("transform",
                    "translate(" + (width / 2) + " ," +
                    (height + margin.top + 12) + ")")
                .style("text-anchor", "middle")
                .text("% of participants, sorted by per capita emission");

            svg.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .text("% of total emissions");

            let barSettings = [];
            emissionsPerGroup.forEach((element, index) => {
                let bottomBorder;
                let leftBorder;
                if (index === 0) {
                    bottomBorder = 0;
                    leftBorder = 0;
                }
                else {
                    bottomBorder = emissionsPerGroup[index - 1] / emissionsSum * 100.0;
                    leftBorder = attendeeNumberPerGroup[index - 1] / attendeeSum * 100.0;
                }
                barSettings[index] =
                    {
                        topBorder: emissionsPerGroup[index] / emissionsSum * 100.0,
                        bottomBorder: bottomBorder,
                        leftBorder: leftBorder,
                        rightBorder: attendeeNumberPerGroup[index] / attendeeSum * 100.0,
                    };
                // console.log(index);
                // console.log(barSettings[index]);
            });
            // console.log(barSettings);
            svg.selectAll("rect")
                .data(barSettings)
                .enter()
                .append("rect")
                .attr("x", 1)
                .attr("transform", function (d) {
                    return "translate(" + x(d.leftBorder) + "," + y(d.topBorder) + ")";
                })
                .attr("width", function (d) {
                    return x(d.rightBorder) - x(d.leftBorder) - 1;
                })
                .attr("height", function (d) {
                    return (y(d.bottomBorder) - y(d.topBorder));
                })
                .style("z-index", "500")
                .style("fill", "#4444E5");
            addVerticalLineAndListenCursor(x, y, barSettings);
        }));


    });

}