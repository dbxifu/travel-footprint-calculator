// jQuery-free
function draw_emissions_equidistant_map(containerSelector, worldDataUrl, countriesDataUrl, emissionsDataUrl) {
    let margin = {top: 48, right: 88, bottom: 68, left: 98},
        width = 960 - margin.left - margin.right,
        height = 540 - margin.top - margin.bottom;
    const baseAttendeeCircleRadius = 2;
    const legendAmount = 5;
    const baseAttendeeCircleRadiusRatio = 10.0;
    const baseAttendeeCircleColorRatio = 1500.0;

    let emissionsData = null;
    let worldData = null;

    let svg = null;
    let cartaContainer = null;

    let geoPath = d3.geoPath();
    let mapProjection = null;
    let center_latitude = 0.0;
    let center_longitude = 0.0;

    // Per city
    let maxAttendeeAmount = 0;
    let maxFootprint = 0;

    // let coordinatesFromFile = null;
    // let geoJsonFromFile = null;

    // let attendeeAmountPerCountry = [];
    // let countryCoordinates = [];


    // let rotateForm = document.createElement("select");

    // let processGeoJson = function (geojson, firstRead = true) {
    //     geoJsonFromFile = geojson;
    //     cartaContainer.selectAll("path")
    //         .data(geojson.features)
    //         .enter()
    //         .append("path")
    //         .attr("d", geoPath)
    //         .style("fill", "#444444AA");
    //     if (firstRead) {
    //         // Prepare country data
    //         geojson.features.forEach((element) => {
    //             let countryFound = false;
    //             coordinatesFromFile.forEach((countryCoord) => {
    //                 if (countryFound) {
    //                     return;
    //                 }
    //                 if (countryCoord.country === element.properties.iso_a2 || countryCoord.country === element.properties.wb_a2) {
    //                     countryCoordinates.push({
    //                         name: element.properties.name_long,
    //                         latitude: countryCoord.latitude,
    //                         longitude: countryCoord.longitude
    //                     });
    //                     countryFound = true;
    //                 }
    //             });
    //             if (!countryFound) {
    //                 console.log("missing country:" + element.properties.name_long + " by the alpha2:" + element.properties.iso_a2 + " or " + element.properties.wb_a2);
    //             }
    //         });
    //
    //         // Sort country data
    //         function compare(a, b) {
    //             if (a.name < b.name) {
    //                 return -1;
    //             }
    //             if (a.name > b.name) {
    //                 return 1;
    //             }
    //             return 0;
    //         }
    //
    //         countryCoordinates.sort(compare);
    //         // Create Option Elements
    //         countryCoordinates.forEach((element) => {
    //             let option = document.createElement("option");
    //             option.text = element.name;
    //             option.value = JSON.stringify([
    //                 element.latitude,
    //                 element.longitude,
    //             ]);
    //             rotateForm.append(option);
    //         });
    //         // Read actual data Sample
    //         d3.csv(emissionsDataUrl, onEmissionsDatum)
    //             .then(onEmissionsReady);
    //     }
    // };


    // let processCountryCoords = function (countryCoords) {
    //     coordinatesFromFile = countryCoords;
    //     if (geoJsonFromFile) {
    //         processGeoJson(geoJsonFromFile, false);
    //         onEmissionsReady();
    //     } else {
    //         d3.json(worldDataUrl).then(processGeoJson);
    //     }
    //     let selector = containerSelector.slice(1, containerSelector.length);
    //     document.getElementById(selector).insertAdjacentElement("beforeend", rotateForm);
    //     rotateForm.onchange = function (event) {
    //         const [latitude, longitude] = JSON.parse(rotateForm.value);
    //         recenterOnLatLon(latitude, longitude);
    //         // console.log(rotateForm.value);
    //         cartaContainer.remove();
    //         cartaContainer = svg.append("g");
    //         processCountryCoords(coordinatesFromFile, false);
    //     };
    //     // d3.select("svg").on("mousedown", function(event) {
    //     //     console.log(mapProjection.invert(d3.pointer(event)));
    //     // });
    // };


    // const onEmissionsDatum = function (datum) {
    //     let trainAttendee = parseInt(datum["train trips_amount"]);
    //     let planeAttendee = parseInt(datum["plane trips_amount"]);
    //     if (trainAttendee === 0 && planeAttendee === 0) {
    //         return;
    //     }
    //     let attendeeAmount = trainAttendee + planeAttendee;
    //     let distance_km = datum.distance_km / attendeeAmount;
    //     let co2_kg = parseFloat(datum.co2_kg);
    //     if (co2_kg === "NaN" || distance_km === "NaN") {
    //         return;
    //     }
    //     let countryFound = false;
    //     let countryName = datum["country"].slice(1, datum["country"].length);
    //     attendeeAmountPerCountry.forEach((element) => {
    //         if (element.country === countryName) {
    //             element.attendeeAmount += attendeeAmount;
    //             maxAttendeeAmount = Math.max(maxAttendeeAmount, element.attendeeAmount);
    //             countryFound = true;
    //         }
    //
    //     });
    //     if (!countryFound) {
    //         attendeeAmountPerCountry.push({
    //             country: countryName,
    //             attendeeAmount: attendeeAmount
    //         });
    //         maxAttendeeAmount = Math.max(maxAttendeeAmount, attendeeAmount);
    //     }
    // };


    const drawCircle = function (x, y, radius, color, className = "circle") {
        svg.append("circle")
            .attr("class", className)
            .attr("cx", x)
            .attr("cy", y)
            .attr("r", radius)
            .style("fill", color)
            .style("stroke", "rgba(0,0,0,0.7)")
            .style("stroke-width", "1");
    };


    const setupLegend = function () {
        svg.append("rect")
            .attr("class", "legend")
            .attr("transform", "translate(" + 2 + "," + 2 + ")")
            .attr("width", 155)
            .attr("height", legendAmount * 34 + 15)
            .style("fill", "#EEEEEEFF")
            .style("stroke", "#000000")
            .style("stroke-width", "2");
        svg.append("text")
            .attr("class", "legend")
            .attr("transform",
                "translate(" + 50 + " ," +
                (28) + ")")
            .style("text-anchor", "left")
            .text((1).toFixed(0) + " attendees");
        let x = 10 + 20;
        let y = 25;
        let radius = baseAttendeeCircleRadius + (baseAttendeeCircleRadiusRatio / maxAttendeeAmount);
        let color = "rgba(" + (-(baseAttendeeCircleColorRatio / maxAttendeeAmount) + 255.0) +
            ", " + (-(baseAttendeeCircleColorRatio / maxAttendeeAmount) + 255.0) +
            ", 240, 0.7)";
        drawCircle(x, y, radius, color);
        for (let i = 1; i < legendAmount; i++) {
            svg.append("text")
                .attr("class", "legend")
                .attr("transform",
                    "translate(" + 50 + " ," +
                    (28 + 34 * i) + ")")
                .style("text-anchor", "left")
                .text((Math.floor(maxAttendeeAmount * (i / legendAmount))).toFixed(0) + " attendees");
            let x = 10 + 20;
            let y = 25 + 34 * i;
            let radius = baseAttendeeCircleRadius + Math.sqrt(maxAttendeeAmount * (i / legendAmount)) * (baseAttendeeCircleRadiusRatio / maxAttendeeAmount);
            let color = "rgba(" + (-Math.sqrt(maxAttendeeAmount * (i / legendAmount)) * (baseAttendeeCircleColorRatio / maxAttendeeAmount) + 255.0) +
                ", " + (-Math.sqrt(maxAttendeeAmount * (i / legendAmount)) * (baseAttendeeCircleColorRatio / maxAttendeeAmount) + 255.0) +
                ", 240, 0.7)";
            drawCircle(x, y, radius, color, "legend");
        }

        // todo: describe those in the legend
        // svg.append("circle")
        //     .attr("cx", function (d) { return width /2; })
        //     .attr("cy", function (d) { return height/2; })
        //     .attr("r", function (d) { return 25; })
        //     .style("fill", function(d) { return "rgba(255, 0, 0, 0.7)"; });
        // svg.append("circle")
        //     .attr("class", "attendee-dot")
        //     .attr("cx", function (d) { return width /2; })
        //     .attr("cy", function (d) { return height/2; })
        //     .attr("r", function (d) { return 3; })
        //     .style("fill", function(d) { return "rgba(255, 0, 0, 1.0)"; });
    };


    // const onEmissionsReady = function () {
    //     svg.selectAll("circle.attendee-dot").remove();
    //     svg.selectAll("rect.legend").remove();
    //     svg.selectAll("circle.legend").remove();
    //     svg.selectAll("text.legend").remove();
    //
    //     setupLegend();
    //     attendeeAmountPerCountry.forEach((element) => {
    //         countryCoordinates.forEach((coordinate) => {
    //             if (element.country === coordinate.name) {
    //                 let x = mapProjection([coordinate.longitude, coordinate.latitude])[0];
    //                 let y = mapProjection([coordinate.longitude, coordinate.latitude])[1];
    //                 let radius = baseAttendeeCircleRadius + Math.sqrt(element.attendeeAmount) * (baseAttendeeCircleRadiusRatio / maxAttendeeAmount);
    //                 let color = "rgba(" + (-Math.sqrt(element.attendeeAmount) * (baseAttendeeCircleColorRatio / maxAttendeeAmount) + 255.0) +
    //                     ", " + (-Math.sqrt(element.attendeeAmount) * (baseAttendeeCircleColorRatio / maxAttendeeAmount) + 255.0) +
    //                     ", 240, 0.7)";
    //
    //                 drawCircle(x, y, radius, color, "attendee-dot");
    //             }
    //         })
    //     });
    //     svg.append("circle")
    //         .attr("class", "attendee-dot")
    //         .attr("cx", width / 2)
    //         .attr("cy", height / 2)
    //         .attr("r", 3)
    //         .style("fill", "rgba(255, 0, 0, 1.0)");
    // };


    const crunchEmissionsData = () => {
        emissionsData.forEach((datum, idx) => {
            let trainAttendeesAmount = parseInt(datum["train trips_amount"]);
            let planeAttendeesAmount = parseInt(datum["plane trips_amount"]);
            if (trainAttendeesAmount === 0 && planeAttendeesAmount === 0) {
                return;
            }
            let attendeesAmount = trainAttendeesAmount + planeAttendeesAmount;
            maxAttendeeAmount = Math.max(maxAttendeeAmount, attendeesAmount);
            emissionsData[idx].attendeeAmount = attendeesAmount;

            maxFootprint = Math.max(maxFootprint, datum.co2_kg);
        });
    };


    const redrawCentralCircle = () => {
        svg.selectAll("circle.central-dot").remove();

        svg.append("circle")
            .attr("cx", width / 2)
            .attr("cy", height / 2)
            .attr("r", 2)
            .classed("central-dot", true)
            .style("fill", "rgba(255, 0, 0, 0.777)");
    };


    const redrawDistanceCircles = () => {
        // TODO: draw a few circles and a label with the distance for each
        // …
        // or not.
        // We might instead draw the circle under the mouse
    };


    const redrawAttendees = () => {
        svg.selectAll("circle.attendee-dot").remove();

        emissionsData.forEach((datum) => {
            // console.log("Emission datum", datum);
            let x = mapProjection([datum.longitude, datum.latitude])[0];
            let y = mapProjection([datum.longitude, datum.latitude])[1];
            let radius = (
                baseAttendeeCircleRadius
                +
                (
                    baseAttendeeCircleRadiusRatio
                    *
                    Math.sqrt(
                        datum.attendeeAmount
                        /
                        maxAttendeeAmount
                    )
                )
            );
            let color = (
                255.0
                -
                (
                    baseAttendeeCircleColorRatio
                    *
                    Math.sqrt(
                        datum.co2_kg
                        /
                        maxFootprint
                    )
                )
            );
            drawCircle(
                x, y, radius,
                `rgba(${color}, ${color}, 240.0, 0.618)`,
                "attendee-dot"
            );
        });
    };


    const redrawWorldMap = () => {
        cartaContainer.selectAll("path").remove();
        cartaContainer.selectAll("path")
            .data(worldData.features)
            .enter()
            .append("path")
            .attr("d", geoPath)
            .style("fill", "#d5d5d5");
    };


    const rebuildProjection = () => {
        mapProjection = d3.geoAzimuthalEquidistant()
            .scale(79.4188)
            .rotate([
                // Don't ask me why
                -1 * center_longitude,
                -1 * center_latitude,
            ])
            .translate([width / 2, height / 2]);
        geoPath.projection(mapProjection);
    };


    const recenterOnLatLon = (latitude, longitude) => {
        center_latitude = latitude;
        center_longitude = longitude;

        rebuildProjection();
        // Draw in order from back to front
        redrawWorldMap();
        redrawDistanceCircles();
        redrawAttendees();
        redrawCentralCircle();

        //setupLegend();
    };


    document.addEventListener("DOMContentLoaded", () => {
        width = document.querySelector(containerSelector).parentElement.offsetWidth;
        width = width - margin.left - margin.right;
        svg = d3.select(containerSelector)
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        cartaContainer = svg.append("g");
        Promise.all([
            d3.csv(emissionsDataUrl),
            d3.json(worldDataUrl),
        ]).then((allTheData) => {
            [emissionsData, worldData] = allTheData;
            crunchEmissionsData();
            recenterOnLatLon(
                parseFloat(emissionsData[0].latitude),
                parseFloat(emissionsData[0].longitude)
            );
        });

        d3.select(containerSelector+" svg").on("mousedown", function(event) {
            const pointerLonLat = mapProjection.invert(d3.pointer(event));
            recenterOnLatLon(pointerLonLat[1], pointerLonLat[0]);
        });
    });
}