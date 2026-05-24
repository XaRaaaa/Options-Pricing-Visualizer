import { useEffect, useRef } from "react";
import * as d3 from "d3";

/**
 * @param {{
 *  data: Array<{ spot: number, value: number }>,
 *  title: string,
 *  currentSpot?: number | null
 * }} props
 */
export default function GreekChart({ data, title, currentSpot = null }) {
  const svgRef = useRef(null);

  useEffect(() => {
    const width = 720;
    const height = 360;
    const margin = { top: 28, right: 30, bottom: 44, left: 56 };

    const svg = d3.select(svgRef.current);
    svg.attr("viewBox", `0 0 ${width} ${height}`);
    svg.selectAll("*").remove();

    if (!data || data.length === 0) {
      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("class", "chart-empty")
        .text("No curve data yet");
      return;
    }

    const x = d3
      .scaleLinear()
      .domain(d3.extent(data, (d) => d.spot))
      .nice()
      .range([margin.left, width - margin.right]);

    const y = d3
      .scaleLinear()
      .domain(d3.extent(data, (d) => d.value))
      .nice()
      .range([height - margin.bottom, margin.top]);

    const grid = svg.append("g").attr("class", "chart-grid");
    grid
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(
        d3
          .axisLeft(y)
          .ticks(5)
          .tickSize(-(width - margin.left - margin.right))
          .tickFormat("")
      );
    grid
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(
        d3
          .axisBottom(x)
          .ticks(5)
          .tickSize(-(height - margin.top - margin.bottom))
          .tickFormat("")
      );

    const line = d3
      .line()
      .x((d) => x(d.spot))
      .y((d) => y(d.value))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(data)
      .attr("class", "chart-line")
      .attr("d", line);

    svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x));

    svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    svg
      .append("text")
      .attr("class", "chart-title")
      .attr("x", margin.left)
      .attr("y", 18)
      .text(title);

    const focus = svg.append("g").attr("class", "chart-focus").style("display", "none");
    focus.append("circle").attr("r", 4);
    const focusText = focus.append("text").attr("y", -12);

    // Draw current spot marker (vertical line + dot) if requested
    if (currentSpot != null) {
      const nearestIndex = d3.bisector((d) => d.spot).left(data, currentSpot);
      const prev = data[Math.max(0, nearestIndex - 1)] || data[0];
      const next = data[Math.min(data.length - 1, nearestIndex)] || data[data.length - 1];
      const point = Math.abs(currentSpot - prev.spot) < Math.abs(next.spot - currentSpot) ? prev : next;

      svg
        .append("line")
        .attr("class", "current-marker")
        .attr("x1", x(point.spot))
        .attr("x2", x(point.spot))
        .attr("y1", margin.top)
        .attr("y2", height - margin.bottom);

      svg
        .append("circle")
        .attr("class", "current-dot")
        .attr("cx", x(point.spot))
        .attr("cy", y(point.value))
        .attr("r", 4);

      svg
        .append("text")
        .attr("class", "current-label")
        .attr("x", x(point.spot) + 8)
        .attr("y", y(point.value) - 8)
        .text(`${point.value.toFixed(4)}`);
    }

    const bisect = d3.bisector((d) => d.spot).left;

    svg
      .append("rect")
      .attr("class", "chart-overlay")
      .attr("x", margin.left)
      .attr("y", margin.top)
      .attr("width", width - margin.left - margin.right)
      .attr("height", height - margin.top - margin.bottom)
      .on("mousemove", (event) => {
        const [xPos] = d3.pointer(event);
        const xValue = x.invert(xPos);
        const index = bisect(data, xValue, 1);
        const prev = data[index - 1] || data[0];
        const next = data[index] || data[data.length - 1];
        const point = xValue - prev.spot > next.spot - xValue ? next : prev;

        focus.style("display", null);
        focus.attr("transform", `translate(${x(point.spot)},${y(point.value)})`);
        focusText.text(`S ${point.spot.toFixed(2)}  ${point.value.toFixed(4)}`);
      })
      .on("mouseleave", () => focus.style("display", "none"));
  }, [data, title]);

  return <svg ref={svgRef} className="chart" role="img" />;
}
