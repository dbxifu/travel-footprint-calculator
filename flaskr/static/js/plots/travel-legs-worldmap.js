/**
 * Draws a SVG in the DOM element identified by `containerSelector`.
 *
 * Issues
 * ------
 *
 * - No Zoom (spent 4h on this already)
 * - No animations (wait 'til it's polished)
 *
 * @param containerSelector string
 *   CSS selector, like "#d3viz"
 * @param worldDataUrl
 *   A JSON file with reusable world data.
 *   @see /static/public/data/world-earth.geojson
 * @param travelsDataUrl
 *   A CSV file with rows of
 *   - origin_lon
 *   - origin_lat
 *   - destination_lon
 *   - destination_lat
 */
function draw_travel_legs_worldmap(containerSelector, worldDataUrl, travelsDataUrl) {

    document.addEventListener('DOMContentLoaded', () => {
        const margin = {top: 0, right: 0, bottom: 0, left: 0};
        // var width = $(containerSelector).parent().width();
        // var height = width - margin.top - margin.bottom;
        // let width = width - margin.left - margin.right;
        //{#var height = Math.max(300, 600) - margin.top - margin.bottom;#}
        //{#var width = Math.max(880, $(containerSelector).parent().width());#}

        const size_ratio = 0.85;
        let width = 629.0 * size_ratio;
        let height = 604.0 * size_ratio;
        //{#width = 500.0;#}
        //{#height = 400.0;#}

        let offset_x = 0.0;
        let offset_y = 0.0;

        const svg = d3.select(containerSelector)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const projection = d3.geoMercator()
            .scale(85)
            .translate([width / 2.0 + offset_x, height / 2.0 + offset_y]);

        const geopath = d3.geoPath().projection(projection);

        function draw_from_data(worldData, legsData) {
            const link = [];
            legsData.forEach(function (row) {
                source = [+row.origin_lon, +row.origin_lat];
                target = [+row.destination_lon, +row.destination_lat];
                topush = {type: "LineString", coordinates: [source, target]};
                link.push(topush);
            });

            svg.append("g")
                .selectAll("path")
                .data(worldData.features)
                .enter()
                .append("path")
                .attr("fill", "#b8b8b8")
                .attr("d", geopath)
                .style("stroke", "#fff")
                .style("stroke-width", 0);

            svg.selectAll("myPath")
                .data(link)
                .enter()
                .append("path")
                .attr("d", geopath)
                //            .attr("d", function (d) {
                //                return geopath(d);
                //            })
                .style("fill", "none")
                .style("stroke", "#69b3a2")
                .style("stroke-width", 2);

        }

        const worldDataPromise = d3.json(worldDataUrl);
        const travelsDataPromise = d3.csv(travelsDataUrl);
        Promise.all([worldDataPromise, travelsDataPromise]).then((values) => {
            draw_from_data(values[0], values[1]);
        });

    });

}