function draw_emissions_equidistant_map(containerSelector, csvUrl) {
    let margin = {top: 48, right: 88, bottom: 68, left: 98},
        width = 960 - margin.left - margin.right,
        height = 540 - margin.top - margin.bottom;
    const baseAttendeeCircleRadius = 3*0.62;
    const legendAmount = 5;
    const baseAttendeeCircleRadiusRatio = 150.0*0.62;
    const baseAttendeeCircleColorRatio = 1500.0;


    let svg = null;
    let countriesPath = null;
    let geoPath = null;
    let mapProjection = null;

    let coordinatesFromFile = null;
    let geoJsonFromFile = null;

    let attendeeAmountPerCountry = [];
    let countryCoordinates = [];
    let maxAttendeeAmount = 0;

    let rotateForm = document.createElement("select");

    let processGeoJson = function (geojson, firstRead = true) {
        geoJsonFromFile = geojson;
        countriesPath.selectAll("path")
            .data(geojson.features)
            .enter()
            .append("path")
            .attr("d", geoPath)
            .style("fill", "#444444AA");
        if(firstRead)
        {
            // Prepare country data
            geojson.features.forEach((element) => {
                let countryFound = false;
                coordinatesFromFile.forEach((countryCoord) => {
                    if (countryFound) {
                        return;
                    }
                    if (countryCoord.country === element.properties.iso_a2 || countryCoord.country === element.properties.wb_a2) {
                        countryCoordinates.push({
                            name: element.properties.name_long,
                            latitude: countryCoord.latitude,
                            longitude: countryCoord.longitude
                        });
                        countryFound = true;
                    }
                });
                if (!countryFound) {
                    console.log("missing country:" + element.properties.name_long + " by the alpha2:" + element.properties.iso_a2 + " or " + element.properties.wb_a2);
                }
            });

            // Sort country data
            function compare( a, b ) {
                if ( a.name < b.name ){
                    return -1;
                }
                if ( a.name > b.name ){
                    return 1;
                }
                return 0;
            }
            countryCoordinates.sort( compare );
            // Create Option Elements
            countryCoordinates.forEach((element) =>{
                let option = document.createElement("option");
                option.text = element.name;
                option.value = "[ " + -element.longitude + ", " + -element.latitude + "] ";
                rotateForm.append(option);
            });
            // Read actual data Sample
            d3.csv(csvUrl, on_csv_datum)
                .then(on_csv_ready);
        }
    };


    let processCountryCoords = function (countryCoords) {
        coordinatesFromFile = countryCoords;
        if (geoJsonFromFile) {
            processGeoJson(geoJsonFromFile, false);
            on_csv_ready();
        } else {
            d3.json('worldmap.geo.json').then(processGeoJson);

        }
        let selector = containerSelector.slice(1, containerSelector.length);
        document.getElementById(selector).insertAdjacentElement("beforeend", rotateForm);
        rotateForm.onchange = function (event) {
            mapProjection = d3.geoAzimuthalEquidistant().scale(100).rotate(JSON.parse(rotateForm.value)).translate([width/2, height/2]);
            geoPath.projection(mapProjection);
            // console.log(rotateForm.value);
            countriesPath.remove();
            countriesPath = svg.append("g");
            processCountryCoords(coordinatesFromFile, false);
        };
        // d3.select("svg").on("mousedown", function(event) {
        //     console.log(mapProjection.invert(d3.pointer(event)));
        // });
    };


    const on_csv_datum = function (datum) {
        let trainAttendee = parseInt(datum["train trips_amount"]);
        let planeAttendee = parseInt(datum["plane trips_amount"]);
        if (trainAttendee === 0 && planeAttendee === 0) {
            return;
        }
        let attendeeAmount = trainAttendee + planeAttendee;
        let distance_km = datum.distance_km / attendeeAmount;
        let co2_kg = parseFloat(datum.co2_kg);
        if (co2_kg === "NaN" || distance_km === "NaN") {
            return;
        }
        let countryFound = false;
        let countryName = datum["country"].slice(1, datum["country"].length);
        attendeeAmountPerCountry.forEach((element) =>{
           if (element.country === countryName)
           {
               element.attendeeAmount += attendeeAmount;
               maxAttendeeAmount = Math.max(maxAttendeeAmount, element.attendeeAmount);
               countryFound = true;
           }

        });
        if ( ! countryFound ) {
            attendeeAmountPerCountry.push({
                country: countryName,
                attendeeAmount : attendeeAmount
            });
            maxAttendeeAmount = Math.max(maxAttendeeAmount, attendeeAmount);
        }
    };


    const drawCircle = function (x, y, radius, color, className = "legend")
    {
        svg.append("circle")
            .attr("class", className)
            .attr("cx", x)
            .attr("cy", y )
            .attr("r", radius)
            .style("fill", color)
            .style("stroke", "rgba(0,0,0,0.7)")
            .style("stroke-width", "1");
    };


    const setupLegend = function() {
        svg.append("rect")
            .attr("class", "legend")
            .attr("transform", "translate(" + 2 + "," + 2 + ")")
            .attr("width", 150)
            .attr("height", legendAmount * 34 + 15)
            .style("fill", "#EEEEEEFF")
            .style("stroke", "#000000")
            .style("stroke-width", "2");
        svg.append("text")
            .attr("class", "legend")
            .attr("transform",
                "translate(" + 60 + " ," +
                (28) + ")")
            .style("text-anchor", "left")
            .text((1).toFixed(0) + " attendees");
        let x = 10 + 20;
        let y = 25;
        let radius = baseAttendeeCircleRadius + (baseAttendeeCircleRadiusRatio/maxAttendeeAmount);
        let color = "rgba(" + (-(baseAttendeeCircleColorRatio/maxAttendeeAmount) + 255.0) +
            ", " + (-(baseAttendeeCircleColorRatio/maxAttendeeAmount) + 255.0) +
            ", 240, 0.7)";
        drawCircle(x, y, radius, color);
        for (let i = 1; i < legendAmount; i++)
        {
            svg.append("text")
                .attr("class", "legend")
                .attr("transform",
                    "translate(" + 60 + " ," +
                    (28 + 34 * i) + ")")
                .style("text-anchor", "left")
                .text((Math.floor(maxAttendeeAmount * (i / legendAmount))).toFixed(0) + " attendees");
            let x = 10 + 20;
            let y = 25 + 34 * i;
            let radius = baseAttendeeCircleRadius + Math.sqrt(maxAttendeeAmount*(i/legendAmount))*(baseAttendeeCircleRadiusRatio/maxAttendeeAmount);
            let color = "rgba(" + (-Math.sqrt(maxAttendeeAmount*(i/legendAmount))*(baseAttendeeCircleColorRatio/maxAttendeeAmount) + 255.0) +
                ", " + (-Math.sqrt(maxAttendeeAmount*(i/legendAmount))*(baseAttendeeCircleColorRatio/maxAttendeeAmount) + 255.0) +
                ", 240, 0.7)";
            drawCircle(x, y, radius, color);
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


    const on_csv_ready = function () {
        svg.selectAll("circle.attendee-dot").remove();
        svg.selectAll("rect.legend").remove();
        svg.selectAll("circle.legend").remove();
        svg.selectAll("text.legend").remove();

        setupLegend();
        attendeeAmountPerCountry.forEach((element) =>
        {
            countryCoordinates.forEach((coordinate) => {
                if (element.country === coordinate.name)
                {
                    let x = mapProjection([coordinate.longitude, coordinate.latitude])[0];
                    let y = mapProjection([coordinate.longitude, coordinate.latitude])[1];
                    let radius = baseAttendeeCircleRadius + Math.sqrt(element.attendeeAmount)*(baseAttendeeCircleRadiusRatio/maxAttendeeAmount);
                    let color = "rgba(" + (-Math.sqrt(element.attendeeAmount) * (baseAttendeeCircleColorRatio/maxAttendeeAmount) + 255.0) +
                        ", " + (-Math.sqrt(element.attendeeAmount) * (baseAttendeeCircleColorRatio/maxAttendeeAmount) + 255.0) +
                        ", 240, 0.7)";

                    drawCircle(x, y, radius, color, "attendee-dot");
                }
            })
        });
        svg.append("circle")
            .attr("class", "attendee-dot")
            .attr("cx", width /2)
            .attr("cy",  height/2)
            .attr("r", 3)
            .style("fill", "rgba(255, 0, 0, 1.0)");
    };


    document.addEventListener("DOMContentLoaded", () => {
        width = Math.max(880, $(containerSelector).parent().width());
        width = width - margin.left - margin.right;
        svg = d3.select(containerSelector)
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        svg.append("circle")
            .attr("cx", width /2)
            .attr("cy", height/2)
            .attr("r",  25)
            .style("fill", "rgba(255, 0, 0, 0.7)");
        geoPath = d3.geoPath();
        countriesPath = svg.append("g");
        mapProjection = d3.geoAzimuthalEquidistant().scale(100).rotate([-122, -13]).translate([width/2, height/2]);
        geoPath.projection(mapProjection);
        d3.csv('countries-coordinates.csv').then(processCountryCoords);
    });
}