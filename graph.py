import csv
import json

# File paths
input_csv = "supplier_slugs.csv"
output_html = "supplier_graph.html"

# Load data
edges = []
nodes_set = set()

with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        source, target = row[0].strip(), row[1].strip()
        edges.append({"source": source, "target": target})
        nodes_set.add(source)
        nodes_set.add(target)

nodes = [{"id": name} for name in sorted(nodes_set)]

# Generate the HTML content with embedded D3.js
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Supplier Graph</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      height: 100%;
      overflow: hidden;
      font-family: Arial, sans-serif;
    }}
    svg {{
      width: 100vw;
      height: 100vh;
      background-color: #f9f9f9;
    }}
    .node circle {{
      fill: #1f77b4;
      stroke: #fff;
      stroke-width: 1.5px;
    }}
    .link {{
      stroke: #aaa;
      stroke-opacity: 0.6;
      stroke-width: 1.5px;
    }}
    .label {{
      font-size: 12px;
      fill: #333;
      pointer-events: none;
    }}
  </style>
</head>
<body>
<svg></svg>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
  const nodes = {json.dumps(nodes)};
  const links = {json.dumps(edges)};

  const svg = d3.select("svg");
  const width = window.innerWidth;
  const height = window.innerHeight;

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-250))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("class", "link");

  const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 8)
    .attr("class", "node")
    .call(drag(simulation));

  const label = svg.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .attr("class", "label")
    .text(d => d.id);

  simulation.on("tick", () => {{
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    label
      .attr("x", d => d.x + 10)
      .attr("y", d => d.y);
  }});

  function drag(simulation) {{
    return d3.drag()
      .on("start", (event, d) => {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }})
      .on("drag", (event, d) => {{
        d.fx = event.x;
        d.fy = event.y;
      }})
      .on("end", (event, d) => {{
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }});
  }}
</script>
</body>
</html>
"""

# Write the HTML output
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Graph saved to '{output_html}' — open in browser to view.")
