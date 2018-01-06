'use strict';

var width = 960,
    height = 500

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var color = d3.scaleOrdinal(d3.schemeCategory20);

// the variable 'mega_phone_graph' is scripted in the html.
// I may want Python to dynamically generate json, which will be passed
// to this file.

var link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(mega_phone_graph.links.Text.concat(mega_phone_graph.links.Talk))
    .enter().append("line")
        .attr("stroke", "grey")
        .attr("stroke-width", .1);

var node = svg.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(mega_phone_graph.nodes)
    .enter().append("circle")
    .attr("r", function(d){return d.radius;})
    .attr("fill", function(d) {return color(d.color); })
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

// var path = svg.append("svg:g")
//               .selectAll("path")
//               .data(mega_phone_graph.links.Text)
//               .data(mega_phone_graph.links.Talk)
//               .enter().append("svg:path")
//               .attr("class", "link");

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d){return d.id;}))
    .force("collide", d3.forceCollide(4))
    .force("charge", d3.forceManyBody()
                            .distanceMax(110)
                            .distanceMin(50))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .velocityDecay(.6);


var label = svg.selectAll('.names')
        .data(mega_phone_graph.nodes)
        .enter()
        .append("text")
            .text(colored)
            .style("text-anchor", "start")
            .style("fill", "#555")
            .style("font-family", "Arial")
            .style("font-size", 10)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));


// node.append("title")
//     .attr("dx", 10)
//     .attr("dy", ".35em")
//     .text(function(d) { return d.id; });


simulation
    .nodes(mega_phone_graph.nodes)
    .on("tick", ticked);

simulation.force("link")
    .links(mega_phone_graph.links.Text.concat(mega_phone_graph.links.Talk))
    // .distance(function(d){return d.value;});

function colored(d){
    if (d.color === "green" || d.color === "blue") {
        return d.id;
    };
}

// function forcesStrength(d) {
//     if (d.color === "grey") {
//         return -3;
//     } else {
//         return -15;
//     };
// }

function ticked() {
    link
        .attr("x1", function(d){ return d.source.x; })
        .attr("y1", function(d){ return d.source.y; })
        .attr("x2", function(d){ return d.target.x; })
        .attr("y2", function(d){ return d.target.y; });

    node
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
    label
        .attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; });
}

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.5).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0.5);
  d.fx = null;
  d.fy = null;
}